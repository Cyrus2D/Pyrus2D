from lib.math.geom_2d import *

class Object:
    def __init__(self):
        self._pos = Vector2D.invalid()
        self._vel = Vector2D.invalid()
        self._rpos = Vector2D.invalid()

    def pos(self) -> Vector2D:
        return self._pos.copy()  # TODO How it is?!?

    def vel(self) -> Vector2D:
        return self._vel.copy()  # TODO How it is?!?

    def rpos(self):
        return self._rpos

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

    def update_with_world(self, wm):
        self._update_rpos(wm)
        self._update_more_with_full_state(wm)

    def _update_more_with_full_state(self, wm):
        pass

    def _update_rpos(self, wm):
        self._rpos = self._pos - wm.self().pos()
