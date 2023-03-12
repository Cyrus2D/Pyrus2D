from pyrusgeom.geom_2d import *
import pyrusgeom.soccer_math as smath

from lib.debug.debug import log
from lib.rcsc.server_param import ServerParam as SP
from base.tools import Tools
import time
from base.generator_action import ShootAction, BhvKickGen
from lib.action.kick_table import calc_max_velocity
from lib.rcsc.types import GameModeType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.object_player import PlayerObject


debug_shoot = False
max_shoot_time = 0


class BhvShhotGen(BhvKickGen):
    def generator(self, wm: 'WorldModel') -> ShootAction:
        global max_shoot_time
        start_time = time.time()
        self.total_count = 0
        goal_l = Vector2D(SP.i().pitch_half_length(), -SP.i().goal_half_width())
        goal_r = Vector2D(SP.i().pitch_half_length(), +SP.i().goal_half_width())

        goal_l._y += min(1.5, 0.6 + goal_l.dist(wm.ball().pos()) * 0.042)
        goal_r._y -= min(1.5, 0.6 + goal_r.dist(wm.ball().pos()) * 0.042)

        if wm.self().pos().x() > SP.i().pitch_half_length() - 1.0 and wm.self().pos().abs_y() < SP.i().goal_half_width():
            goal_l._x = wm.self().pos().x() + 1.5
            goal_r._x = wm.self().pos().x() + 1.5

        DIST_DIVS = 25
        dist_step = abs(goal_l.y() - goal_r.y()) / (DIST_DIVS - 1)

        for i in range(DIST_DIVS):
            self.total_count += 1
            target_point = Vector2D(goal_l.x(), goal_l.y() + dist_step * i)
            log.sw_log().shoot().add_text( "#shoot {} to {}".format(self.total_count, target_point))
            self.create_shoot(wm, target_point)
        if len(self.candidates) == 0:
            return None

        self.evaluate_courses(wm)
        self.candidates = sorted(self.candidates, key=lambda candidate: candidate.score, reverse=True)
        #
        # end_time = time.time()
        # if end_time - start_time > max_shoot_time:
        #     max_pass_time = end_time - start_time
        # log.sw_log().pass_().add_text( 'time:{} max is {}'.format(end_time - start_time, max_shoot_time))
        return self.candidates[0]

    def create_shoot(self, wm: 'WorldModel', target_point: Vector2D):
        ball_move_angle = (target_point - wm.ball().pos()).th()
        goalie = wm.get_opponent_goalie()
        if goalie is None or (goalie.unum() > 0 and 5 < goalie.pos_count() < 30):
            # TODO  and wm.dirCount( ball_move_angle ) > 3
            log.sw_log().shoot().add_text( "#shoot {} didnt see goalie".format(self.total_count))
            return

        sp = SP.i()

        ball_speed_max = sp.ball_speed_max() if wm.game_mode().type() == GameModeType.PlayOn \
                                                or wm.game_mode().is_penalty_kick_mode() \
            else wm.self().kick_rate() * sp.max_power()

        ball_move_dist = wm.ball().pos().dist(target_point)

        max_one_step_vel = calc_max_velocity(ball_move_angle, wm.self().kick_rate(), wm.ball().vel())
        max_one_step_speed = max_one_step_vel.r()

        first_ball_speed = max((ball_move_dist + 5.0) * (1.0 - sp.ball_decay()), max_one_step_speed, 1.5)

        over_max = False
        while not over_max:
            if first_ball_speed > ball_speed_max - 0.001:
                over_max = True
                first_ball_speed = ball_speed_max

            not_failed = self.check_shoot(wm, target_point, first_ball_speed, ball_move_angle, ball_move_dist)
            if not_failed:
                if first_ball_speed <= max_one_step_speed + 0.001:
                    self.candidates[-1].kick_step = 1

                if self.candidates[-1].goalie_never_reach \
                        and self.candidates[-1].opponent_never_reach:
                    return

            first_ball_speed += 0.3

    def check_shoot(self, wm: 'WorldModel', target_point: Vector2D, first_ball_speed, ball_move_angle: AngleDeg, ball_move_dist):
        sp = SP.i()


        ball_reach_step = int(
            math.ceil(smath.calc_length_geom_series(first_ball_speed, ball_move_dist, sp.ball_decay())))

        if ball_reach_step == -1:
            log.sw_log().shoot().add_text( 'Cant arrive to target')
            return False
        log.sw_log().shoot().add_text( '{} {} {} {} {}'.format(first_ball_speed, ball_move_dist, sp.ball_decay(), smath.calc_length_geom_series(first_ball_speed, ball_move_dist, sp.ball_decay()), math.ceil(smath.calc_length_geom_series(first_ball_speed, ball_move_dist, sp.ball_decay()))))
        course = ShootAction(self.total_count, target_point, first_ball_speed, ball_move_angle, ball_move_dist,
                             ball_reach_step)

        log.sw_log().shoot().add_text( 'course: {}'.format(course))
        if ball_reach_step <= 1:
            course.ball_reach_step = 1
            self.candidates.append(course)
            log.sw_log().shoot().add_text( 'Yes')
            return True
        opponent_x_thr = sp.their_penalty_area_line_x() - 30.0
        opponent_y_thr = sp.penalty_area_half_width()

        for o in range(1, 12):
            opp = wm.their_player(o)
            if opp.unum() < 1:
                log.sw_log().shoot().add_text( '## opp {} can not, unum')
                continue
            if opp.is_tackling():
                log.sw_log().shoot().add_text( '## opp {} can not, tackle')
                continue
            if opp.pos().x() < opponent_x_thr:
                log.sw_log().shoot().add_text( '## opp {} can not, xthr')
                continue
            if opp.pos().abs_y() > opponent_y_thr:
                log.sw_log().shoot().add_text( '## opp {} can not, ythr')
                continue

            if (ball_move_angle - (opp.pos() - wm.ball().pos()).th()).abs() > 90.0:
                log.sw_log().shoot().add_text( '## opp {} can not, angle')
                continue

            if opp.goalie():
                if self.maybe_goalie_catch(opp, course, wm):
                    return False
                log.sw_log().shoot().add_text( '## opp {} can not, goalie catch')
                continue

            if opp.pos_count() > 10:
                log.sw_log().shoot().add_text( '## opp {} can not, pos count')
                continue
            if opp.is_ghost() and opp.pos_count() > 5:
                log.sw_log().shoot().add_text( '## opp {} can not, ghost')
                continue

            if self.opponent_can_reach(opp, course, wm):
                return False
            log.sw_log().shoot().add_text( '## opp {} can not, cant reach')
        self.candidates.append(course)
        return True

    def maybe_goalie_catch(self, goalie: 'PlayerObject', course: ShootAction, wm: 'WorldModel'):
        penalty_area = Rect2D(Vector2D(SP.i().their_penalty_area_line_x(), -SP.i().penalty_area_half_width()),
                              Size2D(SP.i().penalty_area_length(), SP.i().penalty_area_width()))
        CONTROL_AREA_BUF = 0.15
        sp = SP.i()
        ptype = goalie.player_type()
        min_cycle = Tools.estimate_min_reach_cycle(goalie.pos(), ptype.real_speed_max(), wm.ball().pos(),
                                                   course.ball_move_angle)
        if min_cycle < 0:
            return False

        goalie_speed = goalie.vel().r()
        seen_dist_noise = goalie.dist_from_self() * 0.02
        max_cycle = course.ball_reach_step

        for cycle in range(min_cycle, max_cycle):
            ball_pos = smath.inertia_n_step_point(wm.ball().pos(), course.first_ball_vel, cycle, sp.ball_decay())
            if ball_pos.x() > sp.pitch_half_length():
                break
            in_penalty_area = penalty_area.contains(ball_pos)
            control_area = sp._catchable_area if in_penalty_area else ptype.kickable_area()

            inertia_pos = goalie.inertia_point(cycle)
            target_dist = inertia_pos.dist(ball_pos)

            if in_penalty_area:
                target_dist -= seen_dist_noise

            if target_dist - control_area - CONTROL_AREA_BUF < 0.001:
                return True

            dash_dist = float(target_dist)
            if cycle > 1:
                dash_dist -= control_area * 0.9
                dash_dist *= 0.999

            n_dash = ptype.cycles_to_reach_distance(dash_dist)

            if n_dash > cycle + goalie.pos_count():
                continue
            n_turn = 0
            if goalie.body_count() <= 1:
                Tools.predict_player_turn_cycle(ptype, goalie.body(), goalie_speed, target_dist,
                                                (ball_pos - inertia_pos).th(), control_area + 0.1, True)
            n_step = n_turn + n_dash
            if n_turn == 0:
                n_step += 1

            bonus_step = smath.bound(0, goalie.pos_count(), 5) if in_penalty_area else smath.bound(0,
                                                                                                   goalie.pos_count() - 1,
                                                                                                   1)
            if not in_penalty_area:
                bonus_step -= 1

            if n_step <= cycle + bonus_step:
                return True

            if in_penalty_area and n_step <= cycle + goalie.pos_count() + 1:
                course.goalie_never_reach_ = False
        return False

    def opponent_can_reach(self, opponent, course: ShootAction, wm: 'WorldModel'):
        sp = SP.i()
        ptype = opponent.player_type()
        control_area = ptype.kickable_area()
        min_cycle = Tools.estimate_min_reach_cycle(opponent.pos(), ptype.real_speed_max(), wm.ball().pos(),
                                                   course.ball_move_angle)
        if min_cycle < 0:
            return False

        opponent_speed = opponent.vel().r()
        max_cycle = course.ball_reach_step
        maybe_reach = False
        nearest_step_diff = 1000
        for cycle in range(min_cycle, max_cycle):
            ball_pos = smath.inertia_n_step_point(wm.ball().pos(), course.first_ball_vel, cycle, sp.ball_decay())
            inertia_pos = opponent.inertia_point(cycle)
            target_dist = inertia_pos.dist(ball_pos)
            if target_dist - control_area < 0.001:
                return True
            dash_dist = float(target_dist)
            if cycle > 1:
                dash_dist -= control_area * 0.8
            n_dash = ptype.cycles_to_reach_distance(dash_dist)

            if n_dash > cycle + opponent.pos_count():
                continue

            n_turn = 1
            if opponent.body_count() == 0:
                n_turn = Tools.predict_player_turn_cycle(ptype, opponent.body(), opponent_speed, target_dist,
                                                         (ball_pos - inertia_pos).th(), control_area, True)
            n_step =  n_turn + n_dash
            if n_turn == 0:
                n_step += 1
            bonus_step = smath.bound(0, opponent.pos_count(), 1)
            penalty_step = -1

            if opponent.is_tackling():
                penalty_step -= 5

            if n_step <= cycle + bonus_step + penalty_step:
                return True

            if n_step <= cycle + opponent.pos_count() + 1:
                maybe_reach = True
                diff = cycle + opponent.pos_count() - n_step
                if diff < nearest_step_diff:
                    nearest_step_diff = diff
            if maybe_reach:
                course.opponent_never_reach = False

        return False

    def evaluate_courses(self, wm: 'WorldModel'):
        y_dist_thr2 = pow(8.0, 2)

        sp = SP.i()
        goalie = wm.get_opponent_goalie()
        goalie_angle = (goalie.pos() - wm.ball().pos()).th() if goalie else 180.0

        for it in self.candidates:
            score = 1.0

            if it.kick_step == 1:
                score += 50.0

            if it.goalie_never_reach:
                score += 100.0

            if it.opponent_never_reach:
                score += 100.0

            goalie_rate = 1.0
            if goalie.unum() > 0:
                variance2 = 1.0 if it.goalie_never_reach else pow(10.0, 2)
                angle_diff = (it.ball_move_angle - goalie_angle).abs()
                goalie_rate = 1.0 - math.exp(-pow(angle_diff, 2) / (2.0 * variance2) )

            y_rate = 1.0
            if it.target_point.dist2(wm.ball().pos()) > y_dist_thr2:
                y_dist = max(0.0, it.target_point.abs_y() - 4.0 )
                y_rate = math.exp(-pow(y_dist, 2.0) / (2.0 * pow( sp.goal_half_width() - 1.5, 2)))

            score *= goalie_rate
            score *= y_rate
            it.score_ = score
