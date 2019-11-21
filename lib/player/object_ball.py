from lib.math.soccer_math import *
from lib.player.object import *
from lib.rcsc.server_param import ServerParam


# from lib.player.templates import *


class BallObject(Object):
    vel_count_thr = 10
    pos_count_thr = 10
    rpos_count_thr = 5

    def __init__(self, string=None):
        super().__init__()
        self._dist_from_self: float = 10000
        self._angle_from_self = AngleDeg(0.0)
        self._pos = Vector2D.invalid()
        self._vel = Vector2D.invalid()
        if string is None:
            return
        self.init_str(string)

    def init_str(self, string: str):
        data = string.split(" ")
        self._pos = Vector2D(float(data[0]), float(data[1]))
        self._vel = Vector2D(float(data[2]), float(data[3]))

    def _update_more_with_full_state(self, wm):
        self._dist_from_self = wm.self().pos().dist(self._pos)
        self._angle_from_self = (wm.self().pos() - self._pos).th()

    def dist_from_self(self):
        return self._dist_from_self

    def angle_from_self(self):
        return self._angle_from_self

    def velValid(self):  # ToDo : add count need fix
        return self.vel_count() < BallObject.vel_count_thr

    def posValid(self):  # TODO : add Count need fix
        return self.pos_count() < BallObject.pos_count_thr

    def __repr__(self):
        return f"(pos: {self.pos()}) (vel:{self.vel()})"

    def inertia_point(self, cycle: int) -> Vector2D:
        return inertia_n_step_point(self._pos,
                                    self._vel,
                                    cycle,
                                    ServerParam.i().ball_decay())

    def inertia_final_point(self):
        return inertia_final_point(self.pos(),
                                   self.vel(),
                                   ServerParam.i().ball_decay())
