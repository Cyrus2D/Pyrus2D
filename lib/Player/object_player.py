from lib.Player.object import *
from lib.types import SideID


class PlayerObject(Object):
    def __init__(self):
        self._unum = 0
        self._vel = Vector2D(0, 0)
        self._side: SideID = SideID.NEUTRAL
        self._body = AngleDeg(0)

    def body(self):
        return self._body

    def unum(self):
        return self._unum
