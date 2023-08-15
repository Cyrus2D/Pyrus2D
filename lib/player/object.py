from pyrusgeom.geom_2d import *


class Object: # TODO IMPORTANT; Getter functions do not have to return a copy of the value, the reference is enough
    def __init__(self):
        self.pos = Vector2D.invalid()
        self.pos_error = Vector2D(0, 0)
        self.pos_count: int = 1000
        self.possible_poses: list[Vector2D] = []

        self.seen_pos: Vector2D = Vector2D.invalid()
        self.seen_pos_count: int = 1000

        self.heard_pos: Vector2D = Vector2D.invalid()
        self.heard_pos_count: int = 1000

        self.vel = Vector2D.invalid()
        self.vel_error = Vector2D(0, 0)
        self.vel_count: int = 1000

        self.seen_vel: Vector2D = Vector2D.invalid()
        self.seen_vel_count: int = 1000

        self.heard_vel: Vector2D = Vector2D.invalid()
        self.heard_vel_count: int = 100

        self.rpos = Vector2D.invalid()
        self.rpos_error = Vector2D(0, 0)
        self.rpos_count: int = 1000

        self.seen_rpos: Vector2D = Vector2D.invalid()
        self.seen_rpos_error: Vector2D = Vector2D(0, 0)

        self.dist_from_self: float = 0
        self.angle_from_self: AngleDeg = AngleDeg(0)
        self.dist_from_ball: float = 0
        self.angle_from_ball: AngleDeg = AngleDeg(0)

        self.ghost_count: int = 0
        self.pos_history: list[Vector2D] = []

        self.pos_count_thr: Union[None, int] = None
        self.relation_pos_count_thr: Union[None, int] = None
        self.vel_count_thr: Union[None, int] = None

    def vel_valid(self):
        return self.vel_count < self.vel_count_thr

    def pos_valid(self):
        return self.pos_count < self.pos_count_thr

    def rpos_valid(self):
        return self.rpos_count < self.relation_pos_count_thr

    def reverse(self):
        self.pos.reverse()
        self.vel.reverse()
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
        self.rpos = self.pos - wm.self().pos()
        self.rpos_count = 0
        self.seen_rpos = self.pos - wm.self().pos()
        self.dist_from_self: float = wm.self().pos().dist(self.pos)
        self.angle_from_self: AngleDeg = (wm.self().pos() - self.pos).th()
        self.dist_from_ball: float = (wm.ball().pos() - self.pos)
        self.angle_from_ball: AngleDeg = (wm.ball().pos() - self.pos).th()

    def _update_rpos(self, wm):
        self.rpos: Vector2D = self.pos - wm.self().pos()

    def _update_dist_from_self(self, wm):
        self.dist_from_self = self.rpos.r()

    def long_str(self):
        return f'pos: {self.pos}, ' \
               f'pos_error: {self.pos_error}, ' \
               f'pos_count: {self.pos_count}, ' \
               f'seen_pos: {self.seen_pos}, ' \
               f'seen_pos_count: {self.seen_pos_count}, ' \
               f'heard_pos: {self.heard_pos}, ' \
               f'heard_pos_count: {self.heard_pos_count}, ' \
               f'vel: {self.vel}, ' \
               f'vel_error: {self.vel_error}, ' \
               f'vel_count: {self.vel_count}, ' \
               f'seen_vel: {self.seen_vel}, ' \
               f'seen_vel_count: {self.seen_vel_count}, ' \
               f'heard_vel: {self.heard_vel}, ' \
               f'heard_vel_count: {self.heard_vel_count}, ' \
               f'rpos: {self.rpos}, ' \
               f'rpos_error: {self.rpos_error}, ' \
               f'rpos_count: {self.rpos_count}, ' \
               f'seen_rpos: {self.seen_rpos}, ' \
               f'seen_rpos_error: {self.seen_rpos_error}, ' \
               f'dist_from_self: {self.dist_from_self}, ' \
               f'angle_from_self: {self.angle_from_self}, ' \
               f'dist_from_ball: {self.dist_from_ball}, ' \
               f'angle_from_ball: {self.angle_from_ball}, ' \
               f'ghost_count: {self.ghost_count},'

    def __str__(self):
        return f'''pos: {self.pos()} vel:{self.vel()}'''
