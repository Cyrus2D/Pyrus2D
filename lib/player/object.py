from lib.math.geom_2d import *


class Object:
    def __init__(self):
        self._pos = Vector2D.invalid()
        self._vel = Vector2D.invalid()

        self._rpos = Vector2D.invalid()
        self._dist_from_self = 100000

        self._pos_count = 0  # TODO maybe 10000
        self._seen_pos_count = 0  # TODO maybe 10000
        self._seen_pos = Vector2D.invalid()
        self._vel_count = 0  # TODO maybe 10000
        self._seen_vel_count = 0  # TODO maybe 10000
        self._seen_vel = Vector2D.invalid()

    def pos(self) -> Vector2D:
        return self._pos.copy()

    def vel(self) -> Vector2D:
        return self._vel.copy()

    def rpos(self):
        return self._rpos.copy()

    def pos_count(self):
        return self._pos_count

    def rpos_count(self):
        return self._pos_count

    def seen_pos_count(self):
        return self._seen_pos_count

    def seen_pos(self):
        return self._pos.copy()  # TODO should be written again

    def vel_count(self):
        return self._vel_count

    def seen_vel_count(self):
        return self._seen_vel_count

    def seen_vel(self):
        return self._vel.copy()  # TODO should be written again

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
        self._update_dist_from_self(wm)
        self._update_more_with_full_state(wm)

    def _update_more_with_full_state(self, wm):
        pass

    def _update_rpos(self, wm):
        self._rpos = self._pos - wm.self().pos()

    def _update_dist_from_self(self, wm):
        self._dist_from_self = self._rpos.r()

    def dist_from_self(self):
        return self._dist_from_self
