from lib.player.object import *


class BallObject(Object):
    def __init__(self, string=None):
        super().__init__()
        self._dist_from_self: float = 10000
        if string is None:
            return
        self.init_str(string)

    def init_str(self, string: str):
        data = string.split(" ")
        self._pos = Vector2D(float(data[0]), float(data[1]))
        self._vel = Vector2D(float(data[2]), float(data[3]))

    def update_with_world(self, wm):
        self._dist_from_self = wm.self().pos().dist(self._pos)

    def dist_from_self(self):
        return self._dist_from_self

    def __repr__(self):
        return f"(pos: {self.pos()}) (vel:{self.vel()})"
