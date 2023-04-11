from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.soccer_math import bound

from lib.action.basic_actions import NeckAction

from typing import TYPE_CHECKING

from lib.action.neck_scan_field import NeckScanField
from lib.action.neck_scan_players import NeckScanPlayers
from lib.debug.debug import log
from lib.rcsc.server_param import ServerParam

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent

class NeckTurnToBall(NeckAction):
    def __init__(self):
        super().__init__()

    def execute(self, agent: 'PlayerAgent'):
        log.debug_client().add_message('TurnToBall/')
        SP = ServerParam.i()
        wm = agent.world()

        if not wm.ball().pos_valid():
            NeckScanField().execute(agent)
            return True

        my_next = agent.effector().queued_next_self_pos()
        my_body_next = agent.effector().queued_next_self_body()

        ball_next = agent.effector().queued_next_ball_pos()  # TODO IMP FUNC
        ball_angle_next = (ball_next - my_next).th()
        ball_rel_angle_next = ball_angle_next - my_body_next

        next_view_width = agent.effector().queued_next_view_width().width()

        if ball_rel_angle_next.abs() > SP.max_neck_angle() + next_view_width*0.5:
            NeckScanField().execute(agent)
            return True

        if wm.intercept_table().opponent_reach_cycle() <= 1:
            neck_moment = ball_rel_angle_next - wm.self().neck()
            agent.do_turn_neck(neck_moment)
            return True

        view_half = max(0, next_view_width * 0.5 - 10.)

        opp = wm.get_opponent_nearest_to_ball(10)
        mate = wm.get_teammate_nearest_to_ball(10)

        ball_dist = my_next.dist(ball_next)

        if (SP.visible_distance() * 0.7 < ball_dist < 15
                and (wm.kickable_teammate()
                    or wm.kickable_opponent()
                    or (opp and opp.dist_from_ball() < opp.player_type().kickable_area()+0.3)
                    or (mate and mate.dist_from_ball() < mate.player_type().kickable_area() + 0.3)
                )
            ):
            view_half = max(0, next_view_width*0.5 - 20)

        if (len(wm.opponents_from_self()) >= 11
            and (wm.ball().pos().x() > 0
                or wm.ball().pos().abs_y() > SP.pitch_half_width() - 8
                or not opp
                or opp.dist_from_ball() > 3)):
            best_angle = NeckScanPlayers.INVALID_ANGLE

            if ball_dist > SP.visible_distance() - 0.3 or wm.ball().seen_pos_count() > 0:
                min_neck_angle = bound(SP.min_neck_angle(),
                                       ball_rel_angle_next.degree() - view_half,
                                       SP.max_neck_angle())

                max_neck_angle = bound(SP.min_neck_angle(),
                                       ball_rel_angle_next.degree() + view_half,
                                       SP.max_neck_angle())

                best_angle = NeckScanPlayers.get_best_angle(agent, min_neck_angle, max_neck_angle)

            else:
                best_angle = NeckScanPlayers.get_best_angle(agent)

            if best_angle != NeckScanPlayers.INVALID_ANGLE:
                target_angle = best_angle
                neck_moment = AngleDeg(target_angle - my_body_next.degree() - wm.self().neck().degree())

                agent.do_turn_neck(neck_moment)
                return True

        left_rel_angle = bound(SP.min_neck_angle(), ball_rel_angle_next.degree() - view_half, SP.max_neck_angle())
        right_rel_angle = bound(SP.min_neck_angle(), ball_rel_angle_next.degree() + view_half, SP.max_neck_angle())

        left_sum_count = 0
        right_sum_count = 0

        _, left_sum_count, _ = wm.dir_range_count(my_body_next + left_rel_angle, next_view_width)
        _, right_sum_count, _ = wm.dir_range_count(my_body_next + right_rel_angle, next_view_width)

        if left_sum_count > right_sum_count:
            agent.do_turn_neck(left_rel_angle - wm.self().neck().degree())
        else:
            agent.do_turn_neck(right_rel_angle - wm.self().neck().degree())

        return True

































