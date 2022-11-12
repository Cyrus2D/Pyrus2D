from lib.action.turn_to_point import TurnToPoint

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent

class TurnToBall:
    def __init__(self, cycle: int = 1) -> None:
        self._cycle: int = cycle
    
    def execute(self, agent: 'PlayerAgent'):
        if not agent.world().ball().pos_valid():
            return False
        
        ball_point = agent.world().ball().inertia_point(self._cycle)
        return TurnToPoint(ball_point, self._cycle).execute(agent)