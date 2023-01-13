from pyrusgeom.angle_deg import AngleDeg

from lib.player.soccer_action import NeckAction

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class NeckTurnToRelative(NeckAction):
    def __init__(self, rel_angle: Union[AngleDeg, float]):
        self._angle_rel_to_body: AngleDeg = AngleDeg(rel_angle)

    def execute(self, agent: 'PlayerAgent'):
        return agent.do_turn_neck(self._angle_rel_to_body - agent.world().self().neck())