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
            self._origin = args[0]
            self._direction = args[1]
            self._is_valid = True
        elif len(args) == 2 and isinstance(args[1], Vector2D):
            self._origin = args[0]
            self._direction = (args[1] - args[0]).th()
            self._is_valid = True
        else:
            self._origin = Vector2D()
            self._direction = AngleDeg()
            self._is_valid = True

    """
      \ brief get origin point
      \ return const reference to the member variable
    """

    def origin(self):
        return self._origin

    """
      \ brief get the angle of this ray line
      \ return const reference to the member variable
    """

    def dir(self):
        return self._direction

    """
      \ brief get line generated from this ray
      \ return new line object
    """

    def line(self):
        return Line2D(self._origin, self._direction)

    """
      \ brief check whether p is on the direction of this Ray
      \ param point considered point
      \ param thr threshold angle buffer
      \ return true or false        
    """

    def inRightDir(self, point: Vector2D, thr=10.0):
        return ((point - self._origin).th() - self._direction).abs() < thr

    """
        Line2D
      \ brief get the intersection point with 'line'
      \ param other considered line
      \ return intersection point. if it does not exist, the invalidated value vector is returned.
        Ray2D
      \ brief get the intersection point with 'ray'
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
      \ brief make a logical print.
      \ return print_able str
        origin point + direction Angle Deg
    """

    def __repr__(self):
        return str(self._origin) + " dir : " + str(self._direction)


def test():
    a = Ray2D(Vector2D(5, 10), Vector2D(10, 10))
    print(a)
    b = Ray2D(Vector2D(0, 0), AngleDeg(45))
    print(b)
    c = Ray2D(a._origin, b.dir())
    print(c)


if __name__ == "__main__":
    test()
