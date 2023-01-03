from pyrusgeom.vector_2d import Vector2D

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent
    
class TurnToPoint:
    def __init__(self, point: Vector2D, cycle: int = 1) -> None:
        self._point: Vector2D = point
        self._cycle: int = cycle
        
    def execute(self, agent: 'PlayerAgent'):
        self_player = agent.world().self()
        if not self_player.pos_valid():
            return agent.do_turn(60)
        
        my_point = self_player.inertia_point(self._cycle)
        target_rel_angle = (self._point - my_point).th() - self_player.body()
        
        agent.do_turn(target_rel_angle)
        if target_rel_angle.abs() < 1:
            return False
        return True