"""
  \ file sector_2d.py
  \ brief 2D sector region File.
"""

from lib.math.region_2d import Region2D
from lib.math.vector_2d import Vector2D
from lib.math.angle_deg import AngleDeg
from lib.math.math_values import *


class Sector2D(Region2D):
    """
      \ brief constructor with all variables
      \ param c center point
      \ param min_r smaller radius
      \ param max_r bigger radius
      \ param start start angle(turn clockwise)
      \ param end end angle(turn clockwise)
    """

    def __init__(self, __c: Vector2D, __min_r: float, __max_r: float, __start: AngleDeg, __end: AngleDeg):
        super().__init__()

        self.center = __c
        if __min_r < 0.0:
            self.min_r = 0.0
        else:
            self.min_r = __min_r
        if __min_r > __max_r:
            self.max_r = self.min_r
        else:
            self.max_r = __max_r
        self.start = __start
        self.end = __end
        self.is_valid = True

    """
   \ brief assign new value
   \ param c center point
   \ param min_r smaller radius
   \ param max_r bigger radius
   \ param start start angle(turn clockwise)
   \ param end end angle(turn clockwise)
    """

    def assign(self, __c: Vector2D, __min_r, __max_r, __start: AngleDeg, __end: AngleDeg):
        if type(__end) != AngleDeg:
            __end = AngleDeg(__end)
        if type(__start) != AngleDeg:
            __start = AngleDeg(__start)

        self.center = __c
        if __min_r < 0.0:
            self.min_r = 0.0
        else:
            self.min_r = __min_r
        if __min_r > __max_r:
            self.max_r = self.min_r
        else:
            self.max_r = __max_r
        self.start = __start
        self.end = __end

    """
        \ brief get the center point
        \ return  reference to the member variable
    """

    def center(self):
        return self.center

    """
      \ brief get the small side radius
      \ return  reference to the member variable
    """

    def radiusMin(self):
        return self.min_r

    """
      \ brief get the big side radius
      \ return  reference to the member variable
    """

    def radiusMax(self):
        return self.min_r

    """
      \ brief get the left start angle
      \ return  reference to the member variable
    """

    def angleLeftStart(self):
        return self.start

    """
      \ brief get the right end angle
      \ return  reference to the member variable
    """

    def angleRightEnd(self):
        return self.end

    """
     \ brief calculate the area of self region
     \ return the value of area
    """

    def area(self):
        pass

    """
      \ brief check if point is within self region
      \ param point considered point
      \ return True or False
    """

    def contains(self, point: Vector2D):
        rel = point - self.center
        d2 = rel.r2()
        return (self.min_r * self.min_r <= d2 <= self.max_r * self.max_r and rel.th().isWithin(self.start,
                                                                                               self.end))

    """
         \ brief get smaller side circumference
         \ return the length of circumference
       """

    def getCircumferenceMin(self):
        div = (self.end - self.start).degree()
        if div < 0.0:
            div += 360.0

        return (2.0 * self.min_r * PI) * (div / 360.0)

    """
      \ brief get bigger side circumference
      \ return the length of circumference
    """

    def getCircumferenceMax(self):
        div = (self.end - self.start).degree()
        if div < 0.0:
            div += 360.0

        return (2.0 * self.max_r * PI) * (div / 360.0)

    """
     \ brief make a logical print.
     \ return print_able str
    """

    def __repr__(self):
        return "tmp"


""" """


def test():
    a = Sector2D()
    print(a)


if __name__ == "__main__":
    test()
