from pyrusgeom.geom_2d import *


class Object: # TODO IMPORTANT; Getter functions do not have to return a copy of the value, the reference is enough
    def __init__(self):
        self._pos = Vector2D.invalid()
        self._pos_count: int = 1000

        self._seen_pos: Vector2D = Vector2D.invalid()
        self._seen_pos_count: int = 1000

        self._vel = Vector2D.invalid()
        self._vel_count: int = 1000

        self._seen_vel: Vector2D = Vector2D.invalid()
        self._seen_vel_count: int = 1000

        self._heard_pos: Vector2D = Vector2D.invalid()
        self._heard_pos_count: int = 1000
        self._heard_vel: Vector2D = Vector2D.invalid()

        self._rpos = Vector2D.invalid()
        self._rpos_error = Vector2D(0, 0)
        self._rpos_count: int = 1000
        
        self._dist_from_self: float = 0
        self._angle_from_self: AngleDeg = AngleDeg(0)
        self._dist_from_ball: float = 0
        self._angle_from_ball: AngleDeg = AngleDeg(0)

        self._ghost_count: int = 1000

    def pos(self) -> Vector2D:
        return self._pos.copy()

    def vel(self) -> Vector2D:
        return self._vel.copy()

    def rpos(self) -> Vector2D:
        return self._rpos.copy()

    def pos_count(self) -> int:
        return self._pos_count

    def rpos_count(self) -> int:
        return self._rpos_count

    def seen_pos_count(self) -> int:
        return self._seen_pos_count

    def seen_pos(self) -> Vector2D:
        return self._pos.copy()

    def vel_count(self) -> int:
        return self._vel_count

    def seen_vel_count(self) -> int:
        return self._seen_vel_count

    def seen_vel(self) -> Vector2D:
        return self._vel.copy() 
    
    def heard_pos_count(self) -> int:
        return self._heard_pos_count
    
    def heard_pos(self) -> Vector2D:
        return self._heard_pos

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
        self._rpos: Vector2D = self._pos - wm.self().pos()

    def _update_dist_from_self(self, wm):
        self._dist_from_self = self._rpos.r()

    def dist_from_self(self):
        return self._dist_from_self
    
    def ghost_count(self):
        return self._ghost_count

    def __str__(self):
        return f'''
                pos: {self._pos},
                vel: {self._vel},
                rpos: {self._rpos},
                rpos_error: {self._rpos_error},
                rpos_count: {self._rpos_count},
                dist_from_self: {self._dist_from_self},
                angle_from_self: {self._angle_from_self},
                dist_from_ball: {self._dist_from_ball},
                angle_from_ball: {self._angle_from_ball},
                pos_count: {self._pos_count},
                seen_pos_count: {self._seen_pos_count},
                seen_pos: {self._seen_pos},
                vel_count: {self._vel_count},
                seen_vel_count: {self._seen_vel_count},
                seen_vel: {self._seen_vel},
                ghost_count: {self._ghost_count},
                heard_pos_count: {self._heard_pos_count},
                heard_pos: {self._heard_pos},
                heard_vel: {self._heard_vel},
                '''
