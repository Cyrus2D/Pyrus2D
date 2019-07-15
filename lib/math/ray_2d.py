"""

  \ file ray_2d.py
  \ brief 2D ray line class File.

"""

from lib.math.line_2d import *


class Ray2D:
    """
        AngleDeg:
      \ brief constructor with origin and direction else default constructor. all values are set to 0.
      \ param __o origin point
      \ param __d direction angle
        Vector2D:
      \ brief constructor with origin and direction else default constructor. all values are set to 0.
      \ param __o origin point
      \ param __d direction angle
    """

    def __init__(self, *args):  # , **kwargs):)
        if len(args) == 2 and isinstance(args[1], AngleDeg):
            self.origin = args[0]
            self.direction = args[1]
            self.is_valid = True
        elif len(args) == 2 and isinstance(args[1], Vector2D):
            self.origin = args[0]
            self.direction = (args[1] - args[0]).th()
            self.is_valid = True
        else:
            self.origin = Vector2D()
            self.direction = AngleDeg()
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

    def intersection(self, *args):  # , **kwargs):):
        if len(args) == 1 and isinstance(args[0], Ray2D):
            other = args[0]
            tmp_sol = self.line().intersection(other.line())

            if not tmp_sol.isValid():
                return Vector2D.invalid()

            if not self.inRightDir(tmp_sol) or not other.inRightDir(tmp_sol):
                return Vector2D.invalid()

            return tmp_sol
        if len(args) == 1 and isinstance(args[0], Line2D):
            line = args[0]
            tmp_sol = self.line().intersection(line)

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

    """
      \ brief make a logical print.
      \ return print_able str
        origin point + direction Angle Deg
    """

    def __repr__(self):
        return str(self.origin) + " dir : " + str(self.direction)


def test():
    a = Ray2D(Vector2D(5, 10), Vector2D(10, 10))
    print(a)
    b = Ray2D(Vector2D(0, 0), AngleDeg(45))
    print(b)
    c = Ray2D(a.origin, b.dir())
    print(c)


if __name__ == "__main__":
    test()
