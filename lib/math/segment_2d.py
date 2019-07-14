"""
  \ file segment_2d.py
  \ brief 2D segment line File.
"""

from lib.math.line_2d import *
from lib.math.triangle_2d import *

CALC_ERROR = 1.0e-9


class Segment2D:
    """
      \ brief construct from 2 points
      \ param origin 1st point of segment edge
      \ param terminal 2nd point of segment edge
    """

    def __init__(self, origin: Vector2D, terminal: Vector2D):
        self.origin = origin
        self.terminal = terminal

    """
      \ brief construct directly using raw coordinate values
      \ param origin_x 1st point x value of segment edge
      \ param origin_y 1st point x value of segment edge
      \ param terminal_x 2nd point y value of segment edge
      \ param terminal_y 2nd point y value of segment edge
    """

    def __init__(self, origin_x: float, origin_y: float, terminal_x: float, terminal_y: float):
        self.origin = Vector2D(origin_x, origin_y)
        self.terminal = Vector2D(terminal_x, terminal_y)

    """
      \ brief construct using origin, and length
      \ param origin origin point
      \ param length length of line segment
      \ param direction line direction from origin point
    """

    def __init__(self, origin: Vector2D, length: float, direction: AngleDeg):
        self.origin = origin
        self.terminal = origin + Vector2D.from_polar(length, direction)

    """
      \ brief construct from 2 points
      \ param origin first point
      \ param terminal second point
    """

    def assign(self, origin: Vector2D, terminal: Vector2D):
        self.origin = origin
        self.terminal = terminal

    """
      \ brief construct directly using raw coordinate values
      \ param origin_x 1st point x value of segment edge
      \ param origin_y 1st point x value of segment edge
      \ param terminal_x 2nd point y value of segment edge
      \ param terminal_y 2nd point y value of segment edge
    """

    def assign(self, origin_x: float, origin_y: float, terminal_x: float, terminal_y: float):
        self.origin.assign(origin_x, origin_y)
        self.terminal.assign(terminal_x, terminal_y)

    """
      \ brief construct using origin, and length
      \ param origin origin point
      \ param length length of line segment
      \ param direction line direction from origin point
    """

    def assign(self, origin: Vector2D, length: float, direction: AngleDeg):
        self.origin = origin
        self.terminal = origin + Vector2D.from_polar(length, direction)

    """
      \ brief check if self line segment is valid or not.
      origin's coodinates value have to be different from terminal's one.
      \ return checked result.
    """

    def isValid(self):
        return not self.origin.equalsWeakly(self.terminal)

    """
      \ brief get 1st point of segment edge
      \ return  reference to the vector object
    """

    def origin(self):
        return self.origin

    """
      \ brief get 2nd point of segment edge
      \ return  reference to the vector object
    """

    def terminal(self):
        return self.terminal

    """
      \ brief get line generated from segment
      \ return line object
    """

    def line(self):
        return Line2D(self.origin, self.terminal)

    """
      \ brief get the length of self segment
      \ return distance value
    """

    def length(self):
        return self.origin.dist(self.terminal)

    """
      \ brief get the direction angle of self line segment
      \ return angle object
    """

    def direction(self):
        return (self.terminal - self.origin).th()

    """
      \ brief swap segment edge point
      \ return  reference to self object
    """

    def swap(self):
        tmp = self.origin
        self.origin = self.terminal
        self.terminal = tmp

    """
      \ brief swap segment edge point. This method is equivalent to swap(), for convenience.
      \ return  reference to self object
    """

    def reverse(self):
        return self.swap()

    """
      \ brief get the reversed line segment.
      \ return  reference to self object
    """

    def reversedSegment(self):
        return Segment2D(self.origin, self.terminal).reverse()

    """
      \ brief make perpendicular bisector line from segment points
      \ return line object
    """

    def perpendicularBisector(self):
        return Line2D.perpendicular_bisector(self.origin, self.terminal)

    """
      \ brief check if the point is within the rectangle defined by self segment as a diagonal line.
      \ return True if rectangle contains p
    """

    def contains(self, p: Vector2D):
        return ((p.x - self.origin.x) * (p.x - self.terminal.x) <= CALC_ERROR and (p.y - self.origin.y) * (
                p.y - self.origin.y) <= CALC_ERROR)

    """
      \ brief check if self line segment has completely same value as input line segment.
      \ param other compared object.
      \ return checked result.
    """

    def equals(self, other):
        return self.origin.equals(other.self.origin) and self.terminal.equals(other.self.terminal)

    """
     \ brief check if self line segment has weakly same value as input line segment.
     \ param other compared object.
     \ return checked result.
    """

    def equalsWeakly(self, other):
        return self.origin.equalsWeakly(other.self.origin) and self.terminal.equalsWeakly(other.self.terminal)

    """
      \ brief calculates projection point from p
      \ param p input point
      \ return projection point from p. if it does not exist, the invalidated value vector is returned.
    """

    def projection(self, p: Vector2D):
        direction = self.terminal - self.origin
        length = direction.r()

        if length < EPSILON:
            return self.origin

        direction /= length  # normalize

        d = direction.innerProduct(p - self.origin)
        if -EPSILON < d < length + EPSILON:
            direction *= d
            tmp_vec = Vector2D(self.origin)
            tmp_vec += direction
            return tmp_vec

        return Vector2D.invalid()

    """
      \ brief check & get the intersection point with other line segment
      \ param other checked line segment
      \ param allow_end_point if self value is False, end point is disallowed as an intersection.
      \ return intersection point. if it does not exist, the invalidated value vector is returned.
    """

    def intersection(self, other, allow_end_point: bool):
        sol = self.line().intersection(other.line())

        if not sol.isValid() or not self.contains(sol) or not other.contains(sol):
            return Vector2D.invalid()

        if not allow_end_point and not self.existIntersectionExceptEndpoint(other):
            return Vector2D.invalid()

        return sol

    """
      \ brief check & get the intersection point with other line
      \ param l checked line object
      \ return intersection point. if it does not exist, the invalidated value vector is returned.
    """

    def intersection(self, l: Line2D):
        tmp_line = self.line()
        sol = tmp_line.intersection(l)
        if not sol.isValid() or not self.contains(sol):
            return Vector2D.invalid()
        return sol

    """
      \ brief check if segments cross each other or not.
      \ param other segment for cross checking
      \ return True if self segment crosses, returns False.
    """

    def existIntersection(self, other):
        a0 = Triangle2D.double_signed_area(self.origin, self.terminal, other.origin())
        a1 = Triangle2D.double_signed_area(self.origin, self.terminal, other.terminal())
        b0 = Triangle2D.double_signed_area(other.origin(), other.terminal(), self.origin)
        b1 = Triangle2D.double_signed_area(other.origin(), other.terminal(), self.terminal)

        if a0 * a1 < 0.0 and b0 * b1 < 0.0:
            return True

        if self.origin == self.terminal:
            if other.origin() == other.terminal():
                return self.origin == other.origin()

            return b0 == 0.0 and other.checkIntersectsOnLine(self.origin)

        elif other.origin() == other.terminal():
            return a0 == 0.0 and self.checkIntersectsOnLine(other.origin())

        if a0 == 0.0 and self.checkIntersectsOnLine(other.origin()) or (
                a1 == 0.0 and self.checkIntersectsOnLine(other.terminal())) or (
                b0 == 0.0 and other.checkIntersectsOnLine(self.origin)) or (
                b1 == 0.0 and other.checkIntersectsOnLine(self.terminal)):
            return True

        return False

    """
        \ brief check is that point Intersects On Line
        \ param p Vector2D for that point 
        \ return True and False :D
    """

    def checkIntersectsOnLine(self, p: Vector2D):
        if self.origin.x == self.terminal.x:
            return (self.origin.y <= p.y <= self.terminal.y) or (
                    self.terminal.y <= p.y <= self.origin.y)
        else:
            return (self.origin.x <= p.x <= self.terminal.x) or (
                    self.terminal.x <= p.x <= self.origin.x)

    """
      \ brief check if segments cross each other or not. This method is equivalent to existIntersection(), for convenience.
      \ param other segment for cross checking
      \ return True if self segment crosses, returns False.
    """

    def intersects(self, other):
        return self.existIntersection(other)

    """
      \ brief check if segments intersect each other on non terminal point.
      \ param other segment for cross checking
      \ return True if segments intersect and intersection point is not a
      terminal point of segment.
      False if segments do not intersect or intersect on terminal p oint of segment.
    """

    def existIntersectionExceptEndpoint(self, other):
        return (Triangle2D.double_signed_area(self.origin, self.terminal,
                                              other.origin()) * Triangle2D.double_signed_area(self.origin,
                                                                                              self.terminal,
                                                                                              other.terminal() < 0.0) and (
                        Triangle2D.double_signed_area(other.self.origin, other.terminal(),
                                                      self.origin) * Triangle2D.double_signed_area(other.origin(),
                                                                                                   other.terminal(),
                                                                                                   self.terminal) < 0.0))

    """
      \ brief check if segments intersect each other on non terminal point. This method is equivalent to existIntersectionExceptEndpoint(), for convenience.
      \ param other segment for cross checking
      \ return True if segments intersect and intersection point is not a
      terminal point of segment.
      False if segments do not intersect or intersect on terminal point of segment.
    """

    def intersectsExceptEndpoint(self, other):
        return self.existIntersectionExceptEndpoint(other)

    """
      \ brief check if self line segment intersects with target line.
      \ param l checked line
      \ return checked result
     """

    def existIntersection(self, l: Line2D):
        a0 = l.a() * self.origin.x + l.b() * self.origin.y + l.c()
        a1 = l.a() * self.terminal.x + l.b() * self.terminal.y + l.c()
        return a0 * a1 <= 0.0

    """
      \ brief check if self line segment intersects with target line This method is equivalent to existIntersection(), for convenience. .
      \ param l checked line
      \ return checked result
     """

    def intersects(self, l: Line2D):
        return self.existIntersection(l)

    """
      \ brief get a point on segment where distance of point is minimal.
      \ param p point
      \ return nearest point on segment. if multiple nearest points found.
       returns one of them.
    """

    def nearestPoint(self, p: Vector2D):
        vec_tmp = self.terminal - self.origin

        len_square = vec_tmp.r2()

        if len_square == 0.0:
            return self.origin

        inner_product = vec_tmp.innerProduct((p - self.origin))

        if inner_product <= 0.0:
            return self.origin

        elif inner_product >= len_square:
            return self.terminal

        return self.origin + vec_tmp * inner_product / len_square

    """
      \ brief get minimum distance between self segment and point
      \ param p point
      \ return minimum distance between self segment and point
    """

    def dist(self, p: Vector2D):
        length = self.length()

        if length == 0.0:
            return self.origin.dist(p)

        vec = self.terminal - self.origin
        prod = vec.innerProduct(p - self.origin)

        if 0.0 <= prod <= length * length:
            return math.fabs(Triangle2D.double_signed_area(self.origin, self.terminal, p) / length)

        return math.sqrt(min(self.origin.dist2(p),
                             self.terminal.dist2(p)))

    """
      \ brief get minimum distance between 2 segments
      \ param seg segment
      \ return minimum distance between 2 segments
    """

    def dist(self, seg):
        if self.existIntersection(seg):
            return 0.0

        return min(self.dist(seg.self.origin), self.dist(seg.self.terminal), seg.dist(self.origin),
                   seg.dist(self.terminal))

    """
      \ brief get maximum distance between self segment and point
      \ param p point
      \ return maximum distance between self segment and point
    """

    def farthestDist(self, p: Vector2D):
        return math.sqrt(max(self.origin.dist2(p), self.terminal.dist2(p)))

    """
      \ brief strictly check if point is on segment or not
      \ param p checked point
      \ return True if point is on self segment
    """

    def onSegment(self, p: Vector2D):
        return Triangle2D.double_signed_area(self.origin, self.terminal, p) == 0.0 and self.checkIntersectsOnLine(p)

    """
      \ brief weakly check if point is on segment or not
      \ param p checked point
      \ return True if point is on self segment
    """

    def onSegmentWeakly(self, p: Vector2D):
        proj = self.projection(p)
        return proj.isValid() and p.equalsWeakly(proj)

    """
      \ brief make a logical print.
      \ return print_able str
    """

    def __repr__(self):
        return "{[],[]}".format(self.origin, self.terminal)


def test():
    tri = Triangle2D()
    print(tri)


if __name__ == "__main__":
    test()
