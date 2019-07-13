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
    """

    def __init__(self, __a=1, __b=1, __c=0):
        self.a = __a
        self.b = __b
        self.c = __c
        self.is_valid = True

    """
      \ brief construct from 2 points
      \ param p1 first point
      \ param p2 second point
      ###### OR ######
      \ brief construct from origin point + direction
      \ param org origin point
      \ param linedir direction from origin point      
    """

    def __int__(self, p1_org, p2_linedir):
        self.assign(p1_org, p2_linedir)

    """
      \ brief assign abc value from 2 points
      \ param p1 first point
      \ param p2 second point
    """

    def assign(self, p1: Vector2D, p2: Vector2D):
        self.a = -(p2.y - p1.y)
        self.b = p2.x - p1.x
        self.c = -self.a * p1.x - self.b * p1.y

    """
      \ brief assign abc value t from origin point + direction
      \ param org origin point
      \ param linedir direction from origin point
    """

    def assign(self, org: Vector2D, linedir: AngleDeg):
        self.a = -linedir.sin()
        self.b = linedir.cos()
        self.c = self.a * org.x - self.b * org.y

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
        return Line2D.intersection(self, other)

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
      \ return the intersection point. if no intersection, invalid vector is returned.
    """

    @staticmethod
    def intersection(line1, line2):
        tmp = line1.a() * line2.b() - line1.b() * line2.a()
        if math.fabs(tmp) < EPSILON:
            tmp_vec = Vector2D
            tmp_vec.invalidate()
            return tmp_vec

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
            return Line2D(point1, Vector2D(point1.x + 1.0, point1.y))
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
