"""
  \ file line_2d.py
  \ brief 2D straight line class Source File.

    Line Formula: aX + bY + c = 0
"""

from lib.math.vector_2d import *


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

    def __init__(self, *args):  # , **kwargs):):
        if len(args) == 3:
            self.a = args[0]
            self.b = args[1]
            self.c = args[2]
            self.is_valid = True
        elif len(args) == 2 and isinstance(args[0], Vector2D):
            self.a = 0.0
            self.b = 0.0
            self.c = 0.0
            self.is_valid = True
            self.assign(args[0], args[1])
        else:
            self.a = 0.0
            self.b = 0.0
            self.c = 0.0
            self.is_valid = True

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

    def assign(self, *args):  # , **kwargs):):
        if len(args) == 2 and isinstance(args[1], Vector2D):
            self.a = -(args[1].y - args[0].y)
            self.b = args[1].x - args[0].x
            self.c = -self.a * args[0].x - self.b * args[0].y
        if len(args) == 2 and isinstance(args[1], AngleDeg):
            linedir = args[1]
            self.a = -linedir.sin()
            self.b = linedir.cos()
            self.c = self.a * args[0].x - self.b * args[0].y

    """
      \ brief accessor
      \ return coefficient 'A'  of line formula
    """

    def a(self):
        return self.a

    """
      \ brief accessor
      \ return coefficient 'B'  of line formula
    """

    def b(self):
        return self.b

    """
      \ brief accessor
      \ return coefficient 'C'  of line formula
    """

    def c(self):
        return self.c

    """
      \ brief get X-coordinate correspond to 'y'
      \ param y considered Y
      \ return X coordinate
    """

    def getX(self, y):
        if math.fabs(self.a) < EPSILON:
            return ERROR_VALUE
        return -(self.b * y + self.c) / self.a

    """
      \ brief get Y-coordinate correspond to 'x'
      \ param x considered X
      \ return Y coordinate
    """

    def getY(self, x):
        if math.fabs(self.b) < EPSILON:
            return ERROR_VALUE
        return -(self.a * x + self.c) / self.b

    """
      \ brief calculate distance from point to this line
      \ param p considered point
      \ return distance value
    """

    def dist(self, p: Vector2D):
        return math.fabs((self.a * p.x + self.b * p.y + self.c) / math.sqrt(self.a * self.a + self.b * self.b))

    """
      \ brief get squared distance from this line to point
      \ param p considered point
      \ return squared distance value
    """

    def dist2(self, p: Vector2D):
        d = self.a * p.x + self.b * p.y + self.c
        return (d * d) / (self.a * self.a + self.b * self.b)

    """    
      \ brief check if the slope of this line is same to the slope of 'other'
      \ param other considered line
      \ retval true almost same
      \ retval false not same
    """

    def isParallel(self, other):
        return math.fabs(self.a * other.b() - other.a() * self.b) < EPSILON

    """ 
      \ brief get the intersection point with 'other'
      \ param other considered line
      \ return intersection point. if it does not exist, the invalidated value vector is returned.
    """

    def intersection(self, other):
        return Line2D.Lintersection(self, other)

    """ 
      \ brief calc perpendicular line 
      \ param point the point that perpendicular line pass through
      \ return perpendicular line
    """

    def perpendicular(self, point):
        return Line2D(self.b, -self.a, self.a * point.y - self.b * point.x)

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
    def Lintersection(line1, line2):
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
        return Line2D(origin, AngleDeg.bisect(left, right))

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
            return Line2D(point1, tmp_vec)
        tmp = (point2.x * point2.x - point1.x * point1.x + point2.y * point2.y - point1.y * point1.y) * -0.5
        return Line2D(point2.x - point1.x, point2.y - point1.y, tmp)

    """
      \ brief make a logical print.
      \ return print_able str
        aX + bY + c = 0
    """

    def __repr__(self):
        if self.c == 0:
            return "({} X + {} Y = 0)".format(self.a, self.b)
        return "({} X + {} Y + {} = 0)".format(self.a, self.b, self.c)


def test():
    a = Line2D(1, 1)
    print(a)


if __name__ == "__main__":
    test()
