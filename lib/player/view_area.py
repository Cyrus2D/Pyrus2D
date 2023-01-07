from xmlrpc.client import boolean
from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.vector_2d import Vector2D
from lib.rcsc.game_time import GameTime


class ViewArea:
    def __init__(self,
                 view_width: float = -1,
                 origin: Vector2D = None,
                 angle: AngleDeg = AngleDeg(0),
                 time: GameTime = GameTime(-1, 0)) -> None:
        self._view_width: float = view_width
        self._origin: Vector2D = origin if origin is not None else Vector2D.invalid()
        self._angle: AngleDeg = angle
        self._time: GameTime = time

    def viewWidth(self):
        return self._view_width

    def origin(self):
        return self._origin

    def angle(self):
        return self._angle

    def time(self):
        return self._time

    def is_valid(self) -> boolean:
        return self._view_width > 0
    
    def contains(self, point:Vector2D, dist_thr:float, visible_dist2: float):
        if not self.is_valid():
            return False
        
        rpos = point - self._origin
        if rpos.r2() < visible_dist2:
            return True
        
        return (rpos.th() - self._angle).abs() < self._view_width*0.5 - dist_thr
