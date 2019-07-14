from lib.Player.object import *


class BallObject(Object):
    def __init__(self, string=None):
        super().__init__()
        if string == None:
            return
        self.init_str(string)

    def init_str(self, string: str):
        data = string.split(" ")
        self._pos = Vector2D(int(data[0]), int(data[1]))
        self._vel = Vector2D(int(data[2]), int(data[3]))

    def __repr__(self):
        return f"(pos: {self.pos()}) (vel:{self.vel()})"
