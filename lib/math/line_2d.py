"""
  \ file line_2d.py
  \ brief 2D straight line class Source File.

    Line Formula: aX + bY + c = 0
"""

from lib.math.vector_2d import Vector2D
from lib.math.angle_deg import AngleDeg
import math
from lib.math.math_values import *


class Line2D:
    """
     \ brief construct directly
     \ param __a assigned a value
     \ param __b assigned b value
     \ param __c assigned c value
        2 Vec
     \ brief construct from 2 points
     \ param p1 first point
     \ param p2 second point
        Vec + Ang
     \ brief construct from origin point + direction
     \ param org origin point
     \ param linedir direction from origin point
    """

    def __init__(self,
                 p1: Vector2D = None, p2: Vector2D = None,
                 origin: Vector2D = None, angle: AngleDeg = None,
                 a: float = None, b: float = None, c: float = None):
        self._a = 0.0
        self._b = 0.0
        self._c = 0.0

        self.is_valid = True

        if p1 is not None and p2 is not None:
            self.assign(p1, p2)
        elif angle is not None and origin is not None:
            self.assign(origin=origin, linedir=angle)
        elif (a is not None
                and b is not None
                and c is not None):
            self._a = a
            self._b = b
            self._c = c
        else:
            self.is_valid = False

    """
        Len = 2 / 2 Vector2D
      \ brief assign abc value from 2 points
      \ param p1 first point
      \ param p2 second point
        Len = 2 / AngleDeg
      \ brief assign abc value t from origin point + direction
      \ param org origin point
      \ param linedir direction from origin point
    """

    def assign(self,
               p1: Vector2D = None, p2: Vector2D = None,
               origin: Vector2D = None, linedir: AngleDeg = None):
        if p1 is not None and p2 is not None:
            self._a = -(p2._y - p1._y)
            self._b = p2._x - p1._x
            self._c = -self._a * p1._x - self._b * p1._y
            return self
        if origin is not None and linedir is not None:
            self._a = -linedir.sin()
            self._b = linedir.cos()
            self._c = self._a * origin.x() - self._b * origin.y()

    """
      \ brief accessor
      \ return coefficient 'A'  of line formula
    """

    def a(self):
        return self._a

    """
      \ brief accessor
      \ return coefficient 'B'  of line formula
    """

    def b(self):
        return self._b

    """
      \ brief accessor
      \ return coefficient 'C'  of line formula
    """

    def c(self):
        return self._c

    """
      \ brief get X-coordinate correspond to 'y'
      \ param y considered Y
      \ return X coordinate
    """

    def getX(self, y):
        if math.fabs(self._a) < EPSILON:
            return ERROR_VALUE
        return -(self._b * y + self._c) / self._a

    """
      \ brief get Y-coordinate correspond to 'x'
      \ param x considered X
      \ return Y coordinate
    """

    def getY(self, x):
        if math.fabs(self._b) < EPSILON:
            return ERROR_VALUE
        return -(self._a * x + self._c) / self._b

    """
      \ brief calculate distance from point to this line
      \ param p considered point
      \ return distance value
    """

    def dist(self, p: Vector2D):
        return math.fabs(
            (self._a * p.x() + self._b * p.y() + self._c) / math.sqrt(self._a * self._a + self._b * self._b))

    """
      \ brief get squared distance from this line to point
      \ param p considered point
      \ return squared distance value
    """

    def dist2(self, p: Vector2D):
        d = self._a * p.x() + self._b * p.y() + self._c
        return (d * d) / (self._a * self._a + self._b * self._b)

    """    
      \ brief check if the slope of this line is same to the slope of 'other'
      \ param other considered line
      \ retval true almost same
      \ retval false not same
    """

    def isParallel(self, other):
        return math.fabs(self._a * other.b() - other.a() * self._b) < EPSILON

    """ 
      \ brief get the intersection point with 'other'
      \ param other considered line
      \ return intersection point. if it does not exist, the invalidated value vector is returned.
    """

    def intersection(self, other):
        return Line2D.line_intersection(self, other)

    """ 
      \ brief calc perpendicular line 
      \ param point the point that perpendicular line pass through
      \ return perpendicular line
    """

    def perpendicular(self, point):
        return Line2D(a=self._b, b=-self._a, c=self._a * point.y() - self._b * point.x())

    """
      \ brief calc projection point from p
      \ param p base point
      \ return projection point
    
    """

    def projection(self, point):
        return self.intersection(self.perpendicular(point))

    """  ----------------- static method  ----------------- """

    """
      \ brief get the intersection point of 2 lines
      \ param line1 the first line
      \ param line2 the second line
      \ return the intersection point. if no intersection, invalidated vector is returned.
    """

    @staticmethod
    def line_intersection(line1, line2):
        tmp = line1.a() * line2.b() - line1.b() * line2.a()
        if math.fabs(tmp) < EPSILON:
            return Vector2D.invalid()

        return Vector2D((line1.b() * line2.c() - line2.b() * line1.c()) / tmp,
                        (line2.a() * line1.c() - line1.a() * line2.c()) / tmp)

    """
      \ brief make angle bisector line from two angles
      \ param origin origin point that is passed through by result line
      \ param left left angle
      \ param right right angle
      \ return line object
    """

    @staticmethod
    def angle_bisector(origin, left, right):
        return Line2D(origin=origin, angle=AngleDeg.bisect(left, right))

    """
      \ brief make perpendicular bisector line from twt points
      \ param point1 1st point
      \ param point2 2nd point
      \ return line object
    """

    @staticmethod
    def perpendicular_bisector(point1, point2):
        if math.fabs(point2.x - point1.x) < EPSILON and math.fabs(point2.y - point1.y) < EPSILON:
            print("Error : points have same coordinate values")
            tmp_vec = Vector2D(point1.x + 1, point2.y)
            return Line2D(p1=point1, p2=tmp_vec)
        tmp = (point2.x * point2.x - point1.x * point1.x + point2.y * point2.y - point1.y * point1.y) * -0.5
        return Line2D(a=point2.x - point1.x, b=point2.y - point1.y, c=tmp)

    """
      \ brief make a logical print.
      \ return print_able str
        aX + bY + c = 0
    """

    def __repr__(self):
        if self._c == 0:
            return "({} X + {} Y = 0)".format(self._a, self._b)
        return "({} X + {} Y + {} = 0)".format(self._a, self._b, self._c)


def test():
    a = Line2D(1, 1)
    print(a)


if __name__ == "__main__":
    test()
