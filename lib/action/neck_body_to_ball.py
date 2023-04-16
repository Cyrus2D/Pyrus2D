from pyrusgeom.angle_deg import AngleDeg

from lib.action.neck_body_to_point import NeckBodyToPoint
from lib.action.scan_field import ScanField
from lib.debug.debug import log
from lib.player.soccer_action import NeckAction

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class NeckBodyToBall(NeckAction):
    def __init__(self, angle_buf: Union[AngleDeg,float] = 5.):
        self._angle_buf = float(angle_buf)

    def execute(self, agent: 'PlayerAgent'):
        log.debug_client().add_message('BodyToBall/')
        wm = agent.world()
        if wm.ball().pos_valid():
            ball_next = wm.ball().pos() + wm.ball().vel()

            return NeckBodyToPoint(ball_next, self._angle_buf).execute(agent)
        return ScanField().execute(agent)
