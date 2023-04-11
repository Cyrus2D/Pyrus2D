from pyrusgeom.vector_2d import Vector2D

from lib.action.neck_scan_field import NeckScanField
from lib.debug.debug import log
from lib.player.soccer_action import NeckAction

from typing import TYPE_CHECKING

from lib.rcsc.server_param import ServerParam

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class NeckTurnToPoint(NeckAction):
    def __init__(self, point: Vector2D = None, points: list[Vector2D] = None):
        self._points: list[Vector2D] = []
        if point:
            self._points.append(point)
        else:
            self._points = list(points)

    def execute(self, agent: 'PlayerAgent'):
        log.debug_client().add_message('TurnToPoint/')
        ef = agent.effector()
        wm = agent.world()
        SP = ServerParam.i()

        next_pos = ef.queued_next_self_pos()
        next_body = ef.queued_next_self_body()
        next_view_width = ef.queued_next_view_width().width()/2

        for p in self._points:
            rel_pos = p - next_pos
            rel_angle = rel_pos.th() - next_body

            if rel_angle.abs() < SP.max_neck_angle() + next_view_width - 5.:
                return agent.do_turn_neck(rel_angle - agent.world().self().neck())

        NeckScanField().execute(agent)
        return True














