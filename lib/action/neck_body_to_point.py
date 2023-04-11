from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.soccer_math import bound
from pyrusgeom.vector_2d import Vector2D

from lib.action.neck_turn_to_relative import NeckTurnToRelative
from lib.debug.debug import log
from lib.player.soccer_action import NeckAction

from typing import TYPE_CHECKING, Union

from lib.rcsc.server_param import ServerParam

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class NeckBodyToPoint(NeckAction):
    def __init__(self, point: Vector2D, angle_buf: Union[AngleDeg, float] = 5.):
        super().__init__()
        self._point = point.copy()
        self._angle_buf = float(angle_buf)

    def execute(self, agent: 'PlayerAgent'):
        log.debug_client().add_message('BodyToPoint/')
        SP = ServerParam.i()
        wm = agent.world()

        angle_buf = bound(0., self._angle_buf, 180.)

        my_next = wm.self().pos() + wm.self().vel()
        target_rel_angle = (self._point - my_next).th() - wm.self().body()

        if SP.min_neck_angle() + angle_buf < target_rel_angle.degree() < SP.max_neck_angle() - angle_buf:
            agent.do_turn(0.)
            agent.set_neck_action(NeckTurnToRelative(target_rel_angle))
            return True

        max_turn = wm.self().player_type().effective_turn(SP.max_moment(),wm.self().vel().r())
        if target_rel_angle.abs() < max_turn:
            agent.do_turn(target_rel_angle)
            agent.set_neck_action(NeckTurnToRelative(0.))
            return True

        agent.do_turn(target_rel_angle)
        if target_rel_angle.degree() > 0.:
            target_rel_angle -= max_turn
        else:
            target_rel_angle += max_turn

        agent.set_neck_action(NeckTurnToRelative(target_rel_angle))
        return True


























