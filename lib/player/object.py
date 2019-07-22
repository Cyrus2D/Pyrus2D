from lib.math.geom import *


class Object:
    def __init__(self):
        self._pos = Vector2D.invalid()
        self._vel = Vector2D.invalid()

    def pos(self):
        return self._pos

    def vel(self):
        return self._vel

    def reverse(self):
        self._pos.reverse()
        self._vel.reverse()
        self.reverse_more()

    def reverse_more(self):
        pass

    @staticmethod
    def reverse_list(lst):
        for i in range(len(lst)):
            lst[i].reverse()
