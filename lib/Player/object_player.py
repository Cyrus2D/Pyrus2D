from lib.Player.object import *
from lib.Player.player_type import PlayerType
from lib.types import SideID


class PlayerObject(Object):
    def __init__(self):
        self._unum: int = 0
        self._vel: Vector2D = Vector2D(0, 0)
        self._pos: Vector2D = Vector2D(0, 0)
        self._side: SideID = SideID.NEUTRAL
        self._body: float = AngleDeg(0)
        self._goalie: bool = False
        self._player_type: PlayerType = None

    def body(self):
        return self._body

    def unum(self):
        return self._unum
