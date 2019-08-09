from lib.action.go_to_point import GoToPoint
from lib.math.vector_2d import Vector2D
from lib.player.templates import PlayerAgent, WorldModel


class Intercept:
    def __init__(self, save_recovery: bool = True,
                 face_point: Vector2D = Vector2D.invalid()):
        self._save_recovery = save_recovery
        self._face_point = face_point

    def execute(self, agent: PlayerAgent):
        wm: WorldModel = agent.world()
        GoToPoint(wm.ball().pos(), 1, 100).execute(agent)
