"""
  \ file hold_ball.py
  \ brief stay there and keep the ball from opponent players.
"""
import functools

from lib.debug.debug import log
from lib.debug.level import Level
from pyrusgeom.soccer_math import *
from pyrusgeom.angle_deg import AngleDeg
from lib.action.stop_ball import StopBall
from lib.action.basic_actions import TurnToPoint
from lib.player.soccer_action import BodyAction
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from pyrusgeom.rect_2d import Rect2D
from pyrusgeom.size_2d import Size2D
from pyrusgeom.line_2d import Line2D

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.player_agent import PlayerAgent
    
"""
  \ struct KeepPoint
  \ brief keep point info
 """

DEFAULT_SCORE = 100.0


def KeepPointCmp(item1, item2) -> bool:
    return item1.score_ < item2.score_


class KeepPoint:
    """
      \ brief construct with arguments
      \ param pos global position
      \ param krate kick rate at the position
      \ param score initial score
    """

    def __init__(self, pos=Vector2D.invalid(), kickrate=0.0, score=-10000000.0):
        self.pos_ = pos
        self.kick_rate_ = kickrate
        self.score_ = score

    """
      \ brief reset object value
    """

    def reset(self):
        self.pos_.invalidate()
        self.kick_rate_ = 0.0
        self.score_ = -10000000.0


class HoldBall(BodyAction):
    """
      \ brief accessible from global.
    """

    def __init__(self, do_turn=False, turn_target_point=Vector2D(0.0, 0.0), kick_target_point=Vector2D.invalid()):
        super().__init__()
        self._do_turn = do_turn
        self._turn_target_point = turn_target_point
        self._kick_target_point = kick_target_point

    """
      \ brief execute action
      \ param agent the agent itself
      \ return True if action is performed
    """

    def execute(self, agent: 'PlayerAgent'):
        wm: 'WorldModel' = agent.world()
        if not wm.self().is_kickable():
            log.sw_log().kick().add_text( "not kickable")
            return False

        if not wm.ball().vel_valid():
            return StopBall().execute(agent)

        if self.keepReverse(agent):
            return True

        if self.turnToPoint(agent):
            return True

        if self.keepFront(agent):
            return True

        if self.avoidOpponent(agent):
            return True

        log.sw_log().kick().add_text( "only stop ball")

        return StopBall().execute(agent)

    """
          \ brief kick the ball to avoid opponent
          \ param  agent itself
          \ return True if action is performed
    """

    def avoidOpponent(self, agent: 'PlayerAgent'):
        wm: 'WorldModel' = agent.world()
        point = self.searchKeepPoint(wm)
        if not point.is_valid():
            log.sw_log().kick().add_text( "avoidOpponent() no candidate point")
            return False
        ball_move = point - wm.ball().pos()
        kick_accel = ball_move - wm.ball().vel()
        kick_accel_r = kick_accel.r()
        agent.do_kick(kick_accel_r / wm.self().kick_rate(),
                      kick_accel.th() - wm.self().body())
        return True

    """
      \ brief search the best keep point
      \ param wm  reference to the WorldModel instance
      \ return estimated best keep point. if no point, is returned.
     """

    def searchKeepPoint(self, wm: 'WorldModel'):
        s_last_update_time = GameTime(0, 0)
        s_keep_points = []
        s_best_keep_point = KeepPoint()
        if s_last_update_time != wm.time():
            s_best_keep_point.reset()
            s_keep_points = self.createKeepPoints(wm, s_keep_points)
            self.evaluateKeepPoints(wm, s_keep_points)
            if s_keep_points:
                s_best_keep_point = max(s_keep_points, key=functools.cmp_to_key(KeepPointCmp))
        return s_best_keep_point.pos_

    """
      \ brief create candidate keep points
      \ param wm  reference to the WorldModel instance
      \ param keep_points reference to the variable container
     """

    def createKeepPoints(self, wm: 'WorldModel', candidates):
        param = ServerParam.i()

        max_pitch_x = param.pitch_half_length() - 0.2
        max_pitch_y = param.pitch_half_width() - 0.2

        dir_divs = 20
        dir_step = 360.0 / dir_divs

        near_dist = wm.self().player_type().player_size() + param.ball_size() + wm.self().player_type().kickable_margin() * 0.4
        mid_dist = wm.self().player_type().player_size() + param.ball_size() + wm.self().player_type().kickable_margin() * 0.6
        far_dist = wm.self().player_type().player_size() + param.ball_size() + wm.self().player_type().kickable_margin() * 0.8

        # candidates = [] * dir_divs * 2

        my_next = wm.self().pos() + wm.self().vel()

        my_noise = wm.self().vel().r() * param.player_rand()
        current_dir_diff_rate = (wm.ball().angle_from_self() - wm.self().body()).abs() / 180.0
        current_dist_rate = (
                                    wm.ball().dist_from_self() - wm.self().player_type().player_size() - param.ball_size()) / wm.self().player_type().kickable_margin()
        current_pos_rate = 0.5 + 0.25 * (current_dir_diff_rate + current_dist_rate)
        current_speed_rate = 0.5 + 0.5 * (wm.ball().vel().r() / (param.ball_speed_max() * param.ball_decay()))

        angles = [-180 + a*dir_step for a in range(dir_divs)]
        for d in angles:
            angle = AngleDeg(d)
            dir_diff = (angle - wm.self().body()).abs()
            unit_pos = Vector2D.polar2vector(1.0, angle)

            # near side point
            near_pos = my_next + unit_pos.set_length_vector(near_dist)
            if (near_pos.abs_x() < max_pitch_x
                    and near_pos.abs_y() < max_pitch_y):
                ball_move = near_pos - wm.ball().pos()
                kick_accel = ball_move - wm.ball().vel()

                # can kick to the point by 1 step kick
                if kick_accel.r() < param.max_power() * wm.self().kick_rate():
                    near_krate = wm.self().player_type().kick_rate(near_dist, dir_diff)
                    # can stop the ball by 1 step kick
                    if ball_move.r() * param.ball_decay() < param.max_power() * near_krate:
                        candidates.append(KeepPoint(near_pos,
                                                    near_krate,
                                                    DEFAULT_SCORE))
            # middle point
            mid_pos = my_next + unit_pos.set_length_vector(mid_dist)
            if (mid_pos.abs_x() < max_pitch_x
                    and mid_pos.abs_y() < max_pitch_y):
                ball_move = mid_pos - wm.ball().pos()
                kick_accel = ball_move - wm.ball().vel()
                kick_power = kick_accel.r() / wm.self().kick_rate()

                # can kick to the point by 1 step kick
                if kick_power < param.max_power():
                    # check move noise
                    move_dist = ball_move.r()
                    ball_noise = move_dist * param.ball_rand()

                    max_kick_rand = wm.self().player_type().kick_rand() * (kick_power / param.max_power()) * (
                            current_pos_rate + current_speed_rate)
                    # move noise is small
                    if ((my_noise + ball_noise + max_kick_rand) * 0.95
                            < wm.self().player_type().kickable_area() - mid_dist - 0.1):
                        mid_krate = wm.self().player_type().kick_rate(mid_dist, dir_diff)
                        # can stop the ball by 1 step kick
                        if move_dist * param.ball_decay() < param.max_power() * mid_krate:
                            candidates.append(KeepPoint(mid_pos,
                                                        mid_krate,
                                                        DEFAULT_SCORE))

            # far side point
            far_pos = my_next + unit_pos.set_length_vector(far_dist)
            if (far_pos.abs_x() < max_pitch_x
                    and far_pos.abs_y() < max_pitch_y):
                ball_move = far_pos - wm.ball().pos()
                kick_accel = ball_move - wm.ball().vel()
                kick_power = kick_accel.r() / wm.self().kick_rate()

                # can kick to the point by 1 step kick
                if kick_power < param.max_power():
                    # check move noise
                    move_dist = ball_move.r()
                    ball_noise = move_dist * param.ball_rand()
                    max_kick_rand = wm.self().player_type().kick_rand() * (kick_power / param.max_power()) * (
                            current_pos_rate + current_speed_rate)
                    # move noise is small
                    if ((my_noise + ball_noise + max_kick_rand) * 0.95
                            < wm.self().player_type().kickable_area() - far_dist - 0.1):
                        far_krate = wm.self().player_type().kick_rate(far_dist, dir_diff)
                        # can stop the ball by 1 step kick
                        if move_dist * param.ball_decay():
                            candidates.append(KeepPoint(far_pos,
                                                        far_krate,
                                                        DEFAULT_SCORE))
        return candidates

    """
      \ brief evaluate candidate keep points
      \ param wm  reference to the WorldModel instance
      \ param keep_points reference to the variable container
     """

    def evaluateKeepPoints(self, wm: 'WorldModel', keep_points):
        for it in keep_points:
            it.score_ = self.evaluateKeepPoint(wm, it.pos_)
            if it.score_ < DEFAULT_SCORE:
                it.score_ += it.pos_.dist(wm.ball().pos())
            else:
                it.score_ += it.kick_rate_ * 1000.0

    """
      \ brief evaluate the keep point
      \ param wm  reference to the WorldModel instance
      \ param keep_point keep point value
    """

    def evaluateKeepPoint(self, wm: 'WorldModel',
                          keep_point: Vector2D):
        penalty_area = Rect2D(Vector2D(ServerParam.i().their_penalty_area_line_x(),
                                       - ServerParam.i().penalty_area_half_width()),
                              Size2D(ServerParam.i().penalty_area_length(),
                                     ServerParam.i().penalty_area_width()))
        consider_dist = (ServerParam.i().tackle_dist()
                         + ServerParam.i().default_player_speed_max()
                         + 1.0)
        param = ServerParam.i()
        score = DEFAULT_SCORE

        my_next = wm.self().pos() + wm.self().vel()
        if len(wm.opponents_from_ball()) == 0:
            return score
        for o in wm.opponents_from_ball():
            if o is None or o.player_type() is None:
                continue
            if o.dist_from_ball() > consider_dist:
                break
            if o.pos_count() > 10:
                continue
            if o.is_ghost():
                continue
            if o.is_tackling():
                continue

            player_type = o.player_type()
            opp_next = o.pos() + o.vel()
            control_area = o.player_type().catchable_area() if (
                    o.goalie() and penalty_area.contains(o.pos()) and penalty_area.contains(
                keep_point)) else o.player_type().kickable_area()
            opp_dist = opp_next.dist(keep_point)

            if opp_dist < control_area * 0.5:

                score -= 100.0

            elif opp_dist < control_area + 0.1:

                score -= 50.0

            elif opp_dist < param.tackle_dist() - 0.2:

                score -= 25.0

            if o.body_count() == 0:
                opp_body = o.body()

            elif o.vel().r() > 0.2:  # o.velCount() <= 1 #and
                opp_body = o.vel().th()

            else:
                opp_body = (my_next - opp_next).th()

            #
            # check opponent body line
            #

            opp_line = Line2D(p=opp_next, a=opp_body)
            line_dist = opp_line.dist(keep_point)
            if line_dist < control_area:

                if line_dist < control_area * 0.8:
                    score -= 20.0
                else:
                    score -= 10.0

            player_2_pos = keep_point - opp_next
            player_2_pos.rotate(- opp_body)

            #
            # check tackle probability
            #
            tackle_dist = param.tackle_dist() if (player_2_pos.x() > 0.0) else param.tackle_back_dist()
            if tackle_dist > 1.0e-5:
                tackle_prob = (pow(player_2_pos.abs_x() / tackle_dist,
                                   param.tackle_exponent())
                               + pow(player_2_pos.abs_y() / param.tackle_width(),
                                     param.tackle_exponent()))
                if (tackle_prob < 1.0
                        and 1.0 - tackle_prob > 0.7):  # success probability
                    score -= 30.0

            #
            # check kick or tackle possibility after dash
            #
            max_accel = (param.max_dash_power()
                         * player_type.dash_power_rate()
                         * player_type.effort_max())

            if (player_2_pos.abs_y() < control_area
                    and player_2_pos.x() > 0.0
                    and (player_2_pos.abs_x() < max_accel
                         or (player_2_pos - Vector2D(max_accel, 0.0)).r() < control_area + 0.1)):
                # next kickable
                score -= 20.0
            elif (player_2_pos.abs_y() < param.tackle_width() * 0.7
                  and player_2_pos.x() > 0.0
                  and player_2_pos.x() - max_accel < param.tackle_dist() - 0.25):
                score -= 10.0

        ball_move_dist = (keep_point - wm.ball().pos()).r()
        if ball_move_dist > wm.self().player_type().kickable_area() * 1.6:
            next_ball_dist = my_next.dist(keep_point)
            threshold = wm.self().player_type().kickable_area() - 0.4
            rate = 1.0 - 0.5 * max(0.0, (next_ball_dist - threshold) / 0.4)
            score *= rate
        return score

    """
      \ brief if possible, to face target point
      \ param agent  agent itself
      \ return True if action is performed
    """

    def turnToPoint(self, agent: 'PlayerAgent'):
        param = ServerParam.i()
        max_pitch_x = param.pitch_half_length() - 0.2
        max_pitch_y = param.pitch_half_width() - 0.2
        wm = agent.world()
        my_next = wm.self().pos() + wm.self().vel()
        ball_next = wm.ball().pos() + wm.ball().vel()

        if (ball_next.abs_x() > max_pitch_x
                or ball_next.abs_y() > max_pitch_y):
            return False

        my_noise = wm.self().vel().r() * param.player_rand()
        ball_noise = wm.ball().vel().r() * param.ball_rand()

        next_ball_dist = my_next.dist(ball_next)

        if (next_ball_dist > (wm.self().player_type().kickable_area()
                              - my_noise
                              - ball_noise
                              - 0.15)):
            return False

        face_point = Vector2D(0.0, 0.0)
        face_point.x = param.pitch_half_length() - 5.0

        if self._do_turn:
            face_point = self._turn_target_point
        my_inertia = wm.self().inertia_final_point()
        target_angle = (face_point - my_inertia).th()

        if (wm.self().body() - target_angle).abs() < 5.0:
            return False

        score = self.evaluateKeepPoint(wm, ball_next)
        if score < DEFAULT_SCORE:
            return False

        TurnToPoint(face_point, 100).execute(agent)
        return True

    """
      \ brief keep the ball at body front
      \ param  agent itself
      \ return True if action is performed
    """

    def keepFront(self, agent: 'PlayerAgent'):
        param = ServerParam.i()
        max_pitch_x = param.pitch_half_length() - 0.2
        max_pitch_y = param.pitch_half_width() - 0.2

        wm = agent.world()
        front_keep_dist = wm.self().player_type().player_size() + param.ball_size() + 0.05

        my_next = wm.self().pos() + wm.self().vel()

        front_pos = my_next + Vector2D.polar2vector(front_keep_dist, wm.self().body())

        if (front_pos.abs_x() > max_pitch_x
                or front_pos.abs_y() > max_pitch_y):
            return False

        ball_move = front_pos - wm.ball().pos()
        kick_accel = ball_move - wm.ball().vel()
        kick_power = kick_accel.r() / wm.self().kick_rate()

        # can kick to the point by 1 step kick
        if kick_power > param.max_power():
            return False

        score = self.evaluateKeepPoint(wm, front_pos)

        if score < DEFAULT_SCORE:
            return False

        agent.do_kick(kick_power,
                      kick_accel.th() - wm.self().body())
        return True

    """
      \ brief keep the ball at reverse point from the kick target point
      \ param  agent itself
    """

    def keepReverse(self, agent: 'PlayerAgent'):
        if not self._kick_target_point.is_valid():
            return False

        param = ServerParam.i()
        max_pitch_x = param.pitch_half_length() - 0.2
        max_pitch_y = param.pitch_half_width() - 0.2
        wm = agent.world()

        my_inertia = wm.self().pos() + wm.self().vel()

        my_noise = wm.self().vel().r() * param.player_rand()
        current_dir_diff_rate = (wm.ball().angle_from_self() - wm.self().body()).abs() / 180.0

        current_dist_rate = (wm.ball().dist_from_self()
                             - wm.self().player_type().player_size()
                             - param.ball_size()) / wm.self().player_type().kickable_margin()

        current_pos_rate = 0.5 + 0.25 * (current_dir_diff_rate + current_dist_rate)
        current_speed_rate = 0.5 + 0.5 * (wm.ball().vel().r() / (param.ball_speed_max() * param.ball_decay()))

        keep_angle = (my_inertia - self._kick_target_point).th()
        dir_diff = (keep_angle - wm.self().body()).abs()
        min_dist = (wm.self().player_type().player_size()
                    + param.ball_size()
                    + 0.2)

        keep_dist = wm.self().player_type().player_size() + wm.self().player_type().kickable_margin() * 0.7 + param.ball_size()

        while keep_dist > min_dist:

            keep_pos = my_inertia + Vector2D.polar2vector(keep_dist, keep_angle)

            keep_dist -= 0.05
            if (keep_pos.abs_x() > max_pitch_x
                    or keep_pos.abs_y() > max_pitch_y):
                continue

            ball_move = keep_pos - wm.ball().pos()
            kick_accel = ball_move - wm.ball().vel()
            kick_power = kick_accel.r() / wm.self().kick_rate()

            if kick_power > param.max_power():
                continue

            move_dist = ball_move.r()
            ball_noise = move_dist * param.ball_rand()
            max_kick_rand = wm.self().player_type().kick_rand() * (kick_power / param.max_power()) * (
                    current_pos_rate + current_speed_rate)

            if (my_noise + ball_noise + max_kick_rand) > wm.self().player_type().kickable_area() - keep_dist - 0.1:
                continue

            new_krate = wm.self().player_type().kick_rate(keep_dist, dir_diff)
            if move_dist * param.ball_decay() > new_krate * param.max_power():
                continue

            score = self.evaluateKeepPoint(wm, keep_pos)
            if score >= DEFAULT_SCORE:
                agent.do_kick(kick_power,
                              kick_accel.th() - wm.self().body())
                return True

            return False
