from pyrusgeom.geom_2d import *


class Object: # TODO IMPORTANT; Getter functions do not have to return a copy of the value, the reference is enough
    def __init__(self):
        self._pos = Vector2D.invalid()
        self._pos_error = Vector2D(0, 0)
        self._pos_count: int = 1000
        self._possible_poses: list[Vector2D] = []

        self._seen_pos: Vector2D = Vector2D.invalid()
        self._seen_pos_count: int = 1000

        self._heard_pos: Vector2D = Vector2D.invalid()
        self._heard_pos_count: int = 1000

        self._vel = Vector2D.invalid()
        self._vel_error = Vector2D(0, 0)
        self._vel_count: int = 1000

        self._seen_vel: Vector2D = Vector2D.invalid()
        self._seen_vel_count: int = 1000

        self._heard_vel: Vector2D = Vector2D.invalid()
        self._heard_vel_count: int = 100

        self._rpos = Vector2D.invalid()
        self._rpos_error = Vector2D(0, 0)
        self._rpos_count: int = 1000

        self._seen_rpos: Vector2D = Vector2D.invalid()
        self._seen_rpos_error: Vector2D = Vector2D(0, 0)

        self._dist_from_self: float = 0
        self._angle_from_self: AngleDeg = AngleDeg(0)
        self._dist_from_ball: float = 0
        self._angle_from_ball: AngleDeg = AngleDeg(0)

        self._ghost_count: int = 0
        self._pos_history: list[Vector2D] = []

        self._pos_count_thr: Union[None, int] = None
        self._relation_pos_count_thr: Union[None, int] = None
        self._vel_count_thr: Union[None, int] = None

    def pos(self) -> Vector2D:
        return self._pos.copy()

    def pos_error(self) -> Vector2D:
        return self._pos_error.copy()

    def pos_count(self) -> int:
        return self._pos_count

    def possible_posses(self) -> list[Vector2D]:
        return self._possible_poses

    def seen_pos(self) -> Vector2D:
        return self._seen_pos.copy()

    def seen_pos_error(self) -> Vector2D:
        raise Exception("Object.seen_pos_error is not implemented")

    def seen_pos_count(self) -> int:
        return self._seen_pos_count

    def heard_pos(self) -> Vector2D:
        return self._heard_pos

    def heard_pos_count(self) -> int:
        return self._heard_pos_count

    def vel(self) -> Vector2D:
        return self._vel.copy()

    def vel_error(self) -> Vector2D:
        return self._vel_error.copy()

    def vel_count(self) -> int:
        return self._vel_count

    def seen_vel(self) -> Vector2D:
        return self._seen_vel.copy()

    def seen_vel_count(self) -> int:
        return self._seen_vel_count

    def rpos(self) -> Vector2D:
        return self._rpos.copy()

    def rpos_error(self) -> Vector2D:
        return self._rpos_error.copy()

    def rpos_count(self) -> int:
        return self._rpos_count

    def seen_rpos(self) -> Vector2D:
        return self._seen_rpos

    def seen_rpos_error(self) -> Vector2D:
        return self._seen_rpos_error

    def dist_from_self(self) -> float:
        return self._dist_from_self

    def angle_from_self(self) -> AngleDeg:
        return self._angle_from_self

    def dist_from_ball(self) -> float:
        return self._dist_from_ball

    def angle_from_ball(self) -> AngleDeg:
        return self._angle_from_ball

    def ghost_count(self):
        return self._ghost_count

    def vel_valid(self):
        return self.vel_count() < self._vel_count_thr

    def pos_valid(self):
        return self.pos_count() < self._pos_count_thr

    def rpos_valid(self):
        return self._rpos_count < self._relation_pos_count_thr

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

    def update_more_with_full_state(self, wm: 'WorldModel'):
        self._rpos = self.pos() - wm.self().pos()
        self._rpos_count = 0
        self._seen_rpos = self.pos() - wm.self().pos()
        self._dist_from_self: float = wm.self().pos().dist(self.pos())
        self._angle_from_self: AngleDeg = (wm.self().pos() - self.pos()).th()
        self._dist_from_ball: float = (wm.ball().pos() - self.pos())
        self._angle_from_ball: AngleDeg = (wm.ball().pos() - self.pos()).th()

    def _update_rpos(self, wm):
        self._rpos: Vector2D = self._pos - wm.self().pos()

    def _update_dist_from_self(self, wm):
        self._dist_from_self = self._rpos.r()

    def long_str(self):
        return f'pos: {self._pos}, ' \
               f'pos_error: {self._pos_error}, ' \
               f'pos_count: {self._pos_count}, ' \
               f'seen_pos: {self._seen_pos}, ' \
               f'seen_pos_count: {self._seen_pos_count}, ' \
               f'heard_pos: {self._heard_pos}, ' \
               f'heard_pos_count: {self._heard_pos_count}, ' \
               f'vel: {self._vel}, ' \
               f'vel_error: {self._vel_error}, ' \
               f'vel_count: {self._vel_count}, ' \
               f'seen_vel: {self._seen_vel}, ' \
               f'seen_vel_count: {self._seen_vel_count}, ' \
               f'heard_vel: {self._heard_vel}, ' \
               f'heard_vel_count: {self._heard_vel_count}, ' \
               f'rpos: {self._rpos}, ' \
               f'rpos_error: {self._rpos_error}, ' \
               f'rpos_count: {self._rpos_count}, ' \
               f'seen_rpos: {self._seen_rpos}, ' \
               f'seen_rpos_error: {self._seen_rpos_error}, ' \
               f'dist_from_self: {self._dist_from_self}, ' \
               f'angle_from_self: {self._angle_from_self}, ' \
               f'dist_from_ball: {self._dist_from_ball}, ' \
               f'angle_from_ball: {self._angle_from_ball}, ' \
               f'ghost_count: {self._ghost_count},'
                    # pos_history: {self._pos_history},

    def __str__(self):
        return f'''pos: {self.pos()} vel:{self.vel()}'''

    def heard_vel_count(self):
        return self._heard_vel_count