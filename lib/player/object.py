from lib.math.geom import *


class Object:
    def __init__(self):
        self._pos = Vector2D.invalid()
        self._vel = Vector2D.invalid()

    def pos(self) -> Vector2D:
        return self._pos.copy() # TODO How it is?!?

    def vel(self) -> Vector2D:
        return self._vel.copy() # TODO How it is?!?

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
