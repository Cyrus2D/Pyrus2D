from math import exp

from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.line_2d import Line2D
from pyrusgeom.ray_2d import Ray2D
from pyrusgeom.rect_2d import Rect2D
from pyrusgeom.segment_2d import Segment2D
from pyrusgeom.soccer_math import inertia_final_point, inertia_n_step_point
from pyrusgeom.vector_2d import Vector2D

from base.generator_action import TackleAction
from base.tools import Tools
from lib.rcsc.game_time import GameTime



from typing import TYPE_CHECKING

from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType

if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.object_player import PlayerObject


class TackleGenerator:
    ANGLE_DIVS = 40


    _update_time: GameTime = GameTime()
    _instance = None
    def __init__(self):
        self._candidates: list[TackleAction] = []
        self._best_result: TackleAction = None

    @staticmethod
    def instance() -> 'TackleGenerator':
        if TackleGenerator._instance:
            return TackleGenerator._instance
        TackleGenerator._instance = TackleGenerator()
        return TackleGenerator._instance


    def generate(self, wm: 'WorldModel'):
        if TackleGenerator._update_time == wm.time():
            return

        self._update_time = wm.time().copy()

        self.clear()

        if wm.self().is_kickable():
            return

        if wm.self().tackle_probability() < 0.001 and wm.self().foul_probability() < 0.001:
            return

        if wm.time().stopped_cycle() > 0:
            return

        if wm.game_mode().time() is not GameModeType.PlayOn and not wm.game_mode().is_penalty_kick_mode():
            return

        self.calculate(wm)

    def clear(self):
        self._best_result = TackleAction()
        self._candidates.clear()

    def best_result(self, wm: 'WorldModel'):
        self.generate(wm)
        return self._best_result


    def calculate(self, wm: 'WorldModel'):
        SP = ServerParam.i()

        min_angle = SP.min_moment()
        max_angle = SP.max_moment()
        angle_step = abs(max_angle - min_angle) / TackleGenerator.ANGLE_DIVS

        ball_rel_angle = wm.ball().angle_from_self() - wm.self().body()
        tackle_rate = SP.tackle_power_rate() * (1 - 0.5*ball_rel_angle.abs()/ 180.)

        for a in range(TackleGenerator.ANGLE_DIVS):
            dir = AngleDeg(min_angle + angle_step*a)
            eff_power = SP.max_back_tackle_power() \
                + (SP.max_tackle_power() - SP.max_back_tackle_power()) \
                * (1. - (dir.abs() / 180.))
            eff_power *= tackle_rate

            angle = wm.self().body() + dir
            accel = Vector2D(r=eff_power, a=angle)

            vel = wm.ball().vel() + accel
            speed = vel.r()
            if speed > SP.ball_speed_max():
                vel.set_length(SP.ball_speed_max())

            self._candidates.append(TackleAction(angle, vel))

        self._best_result.clear()

        for tackle in self._candidates:
            tackle._score = self.evaluate(wm, tackle)

            if tackle._score > self._best_result._score:
                self._best_result = tackle

    def evaluate(self, wm, result: TackleAction):
        SP = ServerParam.i()
        ball_end_point = inertia_final_point(wm.ball().pos(),
                                             result._ball_vel,
                                             SP.ball_decay())

        ball_line = Segment2D(wm.ball().pos(), ball_end_point)
        ball_speed = result._ball_speed
        ball_move_angle = result._ball_move_angle

        if ball_end_point.x() > SP.pitch_half_length() \
            and wm.ball().pos().dist2(SP.their_team_goal_pos()) < 20**2:

            goal_line = Line2D(Vector2D(SP.pitch_half_length(), 10),
                               Vector2D(SP.pitch_half_length(), -10))
            intersect = ball_line.intersection(goal_line)
            if intersect and intersect.is_valid() and intersect.abs_y() < SP.goal_half_width():
                shoot_score = 1000000.

                speed_rate = 1. - exp(-ball_speed**2 / (2* (SP.ball_speed_max()/2)**2))
                y_rate = exp(-intersect.abs_y()**2/(2*SP.goal_width()**2))

                shoot_score *= speed_rate * y_rate

                return shoot_score

        if ball_end_point.x() < -SP.pitch_half_length():
            goal_line = Line2D(Vector2D(-SP.pitch_half_length(), 10),
                               Vector2D(-SP.pitch_half_length(), -10))
            intersect = ball_line.intersection(goal_line)
            if intersect and intersect.is_valid() and intersect.abs_y() < SP.goal_half_width() + 1.:
                y_penalty = -10000.0 *exp(-(intersect.abs_y() - SP.goal_half_width())**2 /(2*(SP.ball_speed_max()*0.5)**2))
                speed_bonus = 10000 * exp(-ball_speed**2/(2* (SP.ball_speed_max()*0.5)**2))

                shoot_score = y_penalty + speed_bonus
                return shoot_score

        opponent_reach_step = self.predict_opponents_reach_step(wm, wm.ball().pos(), result._ball_vel, ball_move_angle)
        final_point = inertia_n_step_point(wm.ball().pos(), result._ball_vel, opponent_reach_step, SP.ball_decay())

        final_segment = Segment2D(wm.ball().pos(), final_point)
        pitch = Rect2D.from_center(0., 0., SP.pitch_length(), SP.pitch_width())
        intersections = pitch.intersection(final_segment)

        if len(intersections) > 0:
            final_point = intersections[0]

        our_goal_angle = (SP.our_team_goal_pos() - wm.ball().pos()).th()
        our_goal_angle_diff = (our_goal_angle - ball_move_angle).abs()
        our_goal_angle_rate = 1 - exp(-our_goal_angle_diff**2 / (2*40**2))

        y_rate = 1 \
            if final_point.abs_y() > SP.pitch_half_width() - 0.1 \
            else exp(-(final_point.abs_y() - SP.pitch_half_width())/ (2*SP.pitch_half_width() *0.7) ** 2)

        opp_rate = 1- exp(-opponent_reach_step**2 / (2*30**2))
        score = 10000. *our_goal_angle_rate*y_rate*opp_rate

        return score

    def predict_opponents_reach_step(self,
                                     wm: 'WorldModel',
                                     first_ball_pos: Vector2D,
                                     first_ball_vel: Vector2D,
                                     ball_move_angle: AngleDeg):
        first_min_step = 50

        SP = ServerParam.i()
        ball_end_point = inertia_final_point(first_ball_pos, first_ball_vel, SP.ball_decay())

        if ball_end_point.abs_x() > SP.pitch_half_length() or ball_end_point.abs_y() > SP.pitch_half_width():
            pitch = Rect2D.from_center(0., 0., SP.pitch_length(), SP.pitch_width())
            ball_ray = Ray2D(first_ball_pos, ball_move_angle)

            intersections = pitch.intersection(ball_ray)
            if len(intersections) == 1:
                first_min_step = SP.ball_move_step(first_ball_vel.r(), first_ball_pos.dist(intersections[0]))

        min_step = first_min_step
        for o in wm.their_players():
            step = self.predict_opponent_reach_step(o,
                                                    first_ball_pos,
                                                    first_ball_vel,
                                                    ball_move_angle,
                                                    min_step)

            if step < min_step:
                min_step = step

        return 1000 if min_step == first_min_step else min_step

    def predict_opponent_reach_step(self,
                                    opponent: 'PlayerObject',
                                    first_ball_pos: Vector2D,
                                    first_ball_vel: Vector2D,
                                    ball_move_angle: AngleDeg,
                                    max_cycle):
        SP = ServerParam.i()
        ptype = opponent.player_type()

        opponent_speed = opponent.vel().r()

        min_cycle = Tools.estimate_min_reach_cycle(opponent.pos(),
                                                   ptype.real_speed_max(),
                                                   first_ball_pos,
                                                   ball_move_angle)

        if min_cycle < 0:
            min_cycle = 10

        for cycle in range(min_cycle, max_cycle):
            ball_pos = inertia_n_step_point(first_ball_pos,
                                            first_ball_vel,
                                            cycle,
                                            SP.ball_decay())

            if ball_pos.abs_x() > SP.pitch_half_length() or ball_pos.abs_y() > SP.pitch_half_width():
                return 1000

            inertia_pos = opponent.inertia_point(cycle)
            target_dist = inertia_pos.dist(ball_pos)

            if target_dist - ptype.kickable_area() < 0.001:
                return cycle

            dash_dist = target_dist
            if cycle > 1:
                dash_dist -= ptype.kickable_area()
                dash_dist -= 0.5

            if dash_dist > ptype.real_speed_max()*cycle:
                continue

            n_dash = ptype.cycles_to_reach_distance(dash_dist)
            if n_dash > cycle:
                continue

            n_turn = 0 if opponent.body_count() > 1 else Tools.predict_player_turn_cycle(ptype,
                                                                                         opponent.body(),
                                                                                         opponent_speed,
                                                                                         target_dist,
                                                                                         (ball_pos - inertia_pos).th(),
                                                                                         ptype.kickable_area(),
                                                                                         True)
            n_step = n_turn + n_dash if n_turn == 0 else n_turn + n_dash + 1

            if opponent.is_tackling():
                n_step += 5

            n_step -= min(3, opponent.pos_count())
            if n_step <= cycle:
                return cycle
        return 1000





























