
from typing import TYPE_CHECKING

from pyrusgeom.vector_2d import Vector2D

from lib.player.soccer_action import ViewAction
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType, ViewWidth

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class ViewTactical(ViewAction):
    PREV1 = None
    PREV2 = None

    def __init__(self):
        pass

    def execute(self, agent: 'PlayerAgent'):
        ViewTactical.PREV2 = ViewTactical.PREV1
        ViewTactical.PREV1 = agent.world().self().view_width().width()

        best_width = None
        gm = agent.world().game_mode().type()
        if (gm is GameModeType.BeforeKickOff
            or gm.is_after_goal()
            or gm.is_penalty_setup()
            or gm.is_penalty_ready()
            or gm.is_penalty_miss()
            or gm.is_penalty_score()):

            best_width = ViewWidth.WIDE
        elif gm.is_penalty_taken():
            best_width = ViewWidth.NARROW

        elif gm.is_goalie_catch_ball() and gm.side() == agent.world().our_side():
            best_width = self.get_our_goalie_free_kick_view_width(agent)
        else:
            best_width = self.get_default_view_width(agent)

        if ViewTactical.PREV1 == 180.0 and ViewTactical.PREV2 == 180.0 and agent.world().see_time().cycle() == agent.world().time().cycle() - 2:
            best_width = ViewWidth.WIDE
        elif ViewTactical.PREV1 == 120.0 and best_width.width() == 60.0 and agent.world().see_time().cycle() == agent.world().time().cycle() - 1:
            best_width = ViewWidth.NORMAL

        return agent.do_change_view(best_width)

    def get_default_view_width(self, agent: 'PlayerAgent'):
        wm = agent.world()
        ef = agent.effector()
        SP = ServerParam.i()

        if not wm.ball().pos_valid():
            return ViewWidth.WIDE

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
                    return ViewWidth.WIDE
                if angle_diff > ViewWidth.NARROW.width()/2 -3:
                    return ViewWidth.NORMAL

        if ball_dist > 40:
            return ViewWidth.WIDE

        if ball_dist > 20:
            return ViewWidth.NORMAL

        if ball_dist > 10:
            ball_angle = ef.queued_next_angle_from_body(ef.queued_next_ball_pos())
            if ball_angle.abs() > 120:
                return ViewWidth.WIDE

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

            return ViewWidth.NORMAL
        return ViewWidth.NARROW

    def get_our_goalie_free_kick_view_width(self, agent: 'PlayerAgent'):
        if agent.world().self().goalie():
            return ViewWidth.WIDE
        return self.get_default_view_width(agent)



































