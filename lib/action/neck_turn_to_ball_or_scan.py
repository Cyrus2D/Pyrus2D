from lib.action.neck_scan_field import NeckScanField
from lib.action.neck_turn_to_ball import NeckTurnToBall
from lib.debug.debug import log
from lib.player.soccer_action import NeckAction

from typing import TYPE_CHECKING

from lib.rcsc.server_param import ServerParam

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class NeckTurnToBallOrScan(NeckAction):
    def __init__(self, count_thr: int = 5):
        super().__init__()
        self._count_thr = count_thr

    def execute(self, agent: 'PlayerAgent'):
        log.debug_client().add_message('TurnToBallOrScan/')
        wm = agent.world()
        ef = agent.effector()
        SP = ServerParam.i()

        if wm.ball().pos_count() <= self._count_thr:
            return NeckScanField().execute(agent)

        ball_next = ef.queued_next_ball_pos()
        my_next = ef.queued_next_self_pos()

        if (wm.ball().pos_count() <= 0
                and not wm.kickable_opponent()
                and not wm.kickable_teammate()
                and my_next.dist(ball_next) < SP.visible_distance() - 0.2):
            return NeckScanField().execute(agent)

        my_next_body = ef.queued_next_self_body()
        next_view_width = ef.queued_next_view_width().width()

        if ((ball_next - my_next).th() - my_next_body).abs() > SP.max_neck_angle() + next_view_width * 0.5 + 2:
            return NeckScanField().execute(agent)

        return NeckTurnToBall().execute(agent)













    