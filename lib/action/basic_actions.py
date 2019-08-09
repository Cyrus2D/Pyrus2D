from lib.math.vector_2d import Vector2D
from lib.player.templates import PlayerAgent


class TurnToPoint:
    def __init__(self, point: Vector2D, cycle: int = 1):
        self._point = point
        self._cycle = cycle

    def execute(self, agent: PlayerAgent):
        me = agent.world().self()

        if not me.pos().is_valid():
            return agent.do_turn(60)

        my_point = me.inertia_point(self._cycle)
        target_rel_angle = (self._point - my_point).th() - me.body()

        agent.do_turn(target_rel_angle)
        if target_rel_angle.abs() < 1:
            return False
        return True
