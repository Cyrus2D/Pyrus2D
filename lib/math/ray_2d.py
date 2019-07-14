"""

  \ file ray_2d.py
  \ brief 2D ray line class File.

"""

from lib.math.line_2d import *


class Ray2D:
    """
      \ brief constructor with origin and direction else default constructor. all values are set to 0.
      \ param __o origin point
      \ param __d direction angle
    """

    def __init__(self, __o=Vector2D(0, 0), __d=AngleDeg(0)):
        self.origin = __o
        self.direction = __d
        self.is_valid = True

    """
      \ brief constructor with origin and direction else default constructor. all values are set to 0.
      \ param __o origin point
      \ param __d direction angle
    """

    def __init__(self, __o=Vector2D(), __d=Vector2D()):
        self.origin = __o
        self.direction = (__d - __o).th()
        self.is_valid = True

    """
      \ brief get origin point
      \ return const reference to the member variable
    """

    def origin(self):
        return self.origin

    """
      \ brief get the angle of this ray line
      \ return const reference to the member variable
    """

    def dir(self):
        return self.direction

    """
      \ brief get line generated from this ray
      \ return new line object
    """

    def line(self):
        return Line2D(self.origin, self.direction)

    """
      \ brief check whether p is on the direction of this Ray
      \ param point considered point
      \ param thr threshold angle buffer
      \ return true or false        
    """

    def inRightDir(self, point: Vector2D, thr=10.0):
        return ((point - self.origin).th() - self.direction).abs() < thr

    """
      \ brief get the intersection point with 'line'
      \ param other considered line
      \ return intersection point. if it does not exist, the invalidated value vector is returned.
    """

    def intersection(self, other: Line2D):
        tmp_sol = self.line().intersection(other)

        if not tmp_sol.isValid():
            return Vector2D.invalid()

        if not self.inRightDir(tmp_sol):
            return Vector2D.invalid()

        return tmp_sol

    """
      \ brief get the intersection point with 'ray'
      \ param other considered line
      \ return intersection point. if it does not exist, the invalidated value vector is returned.
    """

    def intersection(self, other):

        tmp_sol = self.line().intersection(other.line())

        if not tmp_sol.isValid():
            return Vector2D.invalid()

        if not self.inRightDir(tmp_sol) or not other.inRightDir(tmp_sol):
            return Vector2D.invalid()

        return tmp_sol

    """
      \ brief make a logical print.
      \ return print_able str
        origin point + direction Angle Deg
    """

    def __repr__(self):
        return str(self.origin) + " dir : " + str(self.direction)


def test():
    a = Vector2D(1, 1)
    print(a)
    b = Vector2D(10, 10)
    print(b)
    c = Ray2D(a, b)
    print(c)


if __name__ == "__main__":
    test()
