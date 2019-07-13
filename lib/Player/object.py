from lib.math.geom import *


class Object:
    def __init__(self):
        self.pos = Vector2D(0, 0)
        self.vel = Vector2D(0, 0)

    def pos(self):
        return self.pos

    def vel(self):
        return self.vel
