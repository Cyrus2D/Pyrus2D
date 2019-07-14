from lib.Player.object import *
from lib.Player.player_type import PlayerType
from lib.Player.stamina import Stamina
from lib.types import SideID, Card


class PlayerObject(Object):
    def __init__(self):
        self._unum: int = 0
        self._pos: Vector2D = Vector2D.invalid()
        self._vel: Vector2D = Vector2D.invalid()
        self._side: SideID = SideID.NEUTRAL
        self._body: AngleDeg = AngleDeg(0)
        self._neck: AngleDeg = AngleDeg(0)
        self._goalie: bool = False
        self._player_type: PlayerType = None
        self._pointto: Vector2D = Vector2D.invalid()
        self._stamina: Stamina = Stamina()
        self._kick: bool = False
        self._tackle: bool = False
        self._charged: bool = False
        self._card: Card = Card.NO_CARD

    def body(self):
        return self._body

    def unum(self):
        return self._unum
