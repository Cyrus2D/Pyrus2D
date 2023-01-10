
from typing import TYPE_CHECKING

from pyrusgeom.vector_2d import Vector2D

from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType, ViewWidth

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class ViewTactical:
    def __init__(self):
        pass

    def execute(self, agent: 'PlayerAgent'):
        gm = agent.world().game_mode().type()
        if (gm is GameModeType.BeforeKickOff
            or gm.is_after_goal()
            or gm.is_penalty_setup()
            or gm.is_penalty_ready()
            or gm.is_penalty_miss()
            or gm.is_penalty_score()):

            return agent.do_change_view(ViewWidth.WIDE)

        if gm.is_penalty_taken():
            return agent.do_change_view(ViewWidth.NARROW)

        if gm.is_goalie_catch_ball():
            if gm.side() == agent.world().our_side():
                return self.do_our_goalie_free_kick(agent)

        return self.do_default(agent)

    def do_default(self, agent: 'PlayerAgent'):
        wm = agent.world()
        ef = agent.effector()
        SP = ServerParam.i()

        if not wm.ball().pos_valid():
            return agent.do_change_view(ViewWidth.WIDE)

        self_min = wm.intercept_table().self_reach_cycle()
        mate_min = wm.intercept_table().teammate_reach_cycle()
        opp_min = wm.intercept_table().opponent_reach_cycle()
        ball_reach_cycle = min(self_min, mate_min, opp_min)

        ball_pos = wm.ball().inertia_point(ball_reach_cycle)
        ball_dist = ef.queued_next_self_pos().dist(ball_pos)

        if wm.self().goalie() and not wm.self().is_kickable():
            goal_pos = Vector2D(- SP.pitch_half_length(), 0)
            if ball_dist > 10 or ball_pos.x() > SP.our_penalty_area_line_x() or ball_pos.dist(goal_pos) > 20:
                ball_angle = ef.queued_next_angle_from_body(ef.queued_next_ball_pos()) # TODO IMP FUNC
                angle_diff = ball_angle.abs() - SP.max_neck_angle()
                if angle_diff > ViewWidth.NORMAL.width()/2 -3:
                    return agent.do_change_view(ViewWidth.WIDE)
                if angle_diff > ViewWidth.NARROW.width()/2 -3:
                    return agent.do_change_view(ViewWidth.NORMAL)

        if ball_dist > 40:
            return agent.do_change_view(ViewWidth.WIDE)

        if ball_dist > 20:
            return agent.do_change_view(ViewWidth.NORMAL)

        if ball_dist > 10:
            ball_angle = ef.queued_next_angle_from_body(ef.queued_next_ball_pos())
            if ball_angle.abs() > 120:
                return agent.do_change_view(ViewWidth.WIDE)

        teammate_ball_dist = 1000.
        opponent_ball_dist = 1000.

        if len(wm.teammates_from_ball()) > 0:
            teammate_ball_dist = wm.teammates_from_ball()[0].dist_from_ball()
        if len(wm.opponents_from_ball()) > 0:
            opponent_ball_dist = wm.opponents_from_ball()[0].dist_from_ball()

        if (not wm.self().goalie()
            and teammate_ball_dist > 5
            and opponent_ball_dist > 5
            and ball_dist > 10
            and wm.ball().dist_from_self() > 10):

            return agent.do_change_view(ViewWidth.NORMAL)
        return agent.do_change_view(ViewWidth.NARROW)

    def do_our_goalie_free_kick(self, agent:'PlayerAgent'):
        if agent.world().self().goalie():
            return agent.do_change_view(ViewWidth.WIDE)
        return self.do_default(agent)



































