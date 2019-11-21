from lib.math.angle_deg import AngleDeg
from lib.math.vector_2d import Vector2D
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import SideID, Card


class GlobalBallObject:
    def __init__(self):
        self._pos: Vector2D = Vector2D(0, 0)
        self._vel: Vector2D = Vector2D(0, 0)

    def pos(self) -> Vector2D:
        return self._pos

    def vel(self) -> Vector2D:
        return self._vel

    def set_pos(self, x, y):
        self._pos.assign(x, y)

    def set_vel(self, x, y):
        self._vel.assign(x, y)


class GlobalPlayerObject:
    def __init__(self):
        self._side: SideID = SideID.NEUTRAL
        self._unum: int = -1
        self._goalie: bool = False
        self._type = -1
        self._player_type: PlayerType = None
        self._pos: Vector2D = Vector2D.invalid()
        self._vel: Vector2D = Vector2D(0, 0)
        self._body: AngleDeg = AngleDeg(0)
        self._face: AngleDeg = AngleDeg(0)
        self._recovery: float = ServerParam.i().recover_init()
        self._pointto_cycle: int = 0
        self._pointto_angle: int = 0
        self._kicket: bool = False
        self._tackle_cycle: int = 0
        self._charged_cycle: int = 0
        self._card: Card = Card.NO_CARD


