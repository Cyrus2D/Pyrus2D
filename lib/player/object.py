from lib.math.geom import *


class Object:
    def __init__(self):
        self._pos = Vector2D.invalid()
        self._vel = Vector2D.invalid()

    def pos(self):
        return self._pos

    def vel(self):
        return self._vel
