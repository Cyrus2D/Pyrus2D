"""
  \ file circle_2d.py
  \ brief 2D circle region File.
"""
from lib.math.segment_2d import Segment2D
from lib.math.ray_2d import Ray2D
from lib.math.vector_2d import Vector2D
from lib.math.line_2d import Line2D
from lib.math.triangle_2d import Triangle2D
import math
from lib.math.math_values import *


"""
  \ brief solve quadratic formula
  \ param a formula constant A
  \ param b formula constant B
  \ param c formula constant C
  \ param sol1 reference to the result variable
  \ param sol2 reference to the result variable
  \ return number of solution
 """


def QUADRATIC_F(a, b, c):
    d = b * b - 4.0 * a * c
    sol1 = 0.0
    sol2 = 0.0
    if math.fabs(d) < EPSILON:
        sol1 = -b / (2.0 * a)
        ans = 1
    elif d < 0.0:
        ans = 0
    else:
        d = math.sqrt(d)
        sol1 = (-b + d) / (2.0 * a)
        sol2 = (-b - d) / (2.0 * a)
        ans = 2
    return [ans, sol1, sol2]


def SQUARE(v):
    return v * v


class Circle2D:
    """
        Default:
      \ brief create a zero area circle at (0,0)
        Input:
      \ brief construct with center point and radius value.
      \ param c center point
      \ param r radius value
    """

    def __init__(self, center=Vector2D(), radius=0.0):
        self._center = center
        self._radius = radius
        if radius < 0.0:
            self._radius = 0.0
        self._is_valid = True

    """
      \ brief assign value.
      \ param c center point
      \ param r radius value
    """

    def assign(self, c: Vector2D, r: float):
        self._center = c
        self._radius = r
        if r < 0.0:
            self._radius = 0.0

    """
      \ brief get the area value of self circle
      \ return value of the area
     """

    def area(self):
        return PI * self._radius * self._radius

    """
      \ brief check if point is within self region
      \ param point considered point
      \ return True if point is contained by self circle
     """

    def contains(self, point: Vector2D):
        return self._center.dist2(point) < self._radius * self._radius

    """
      \ brief get the center point
      \ return center point coordinate value
     """

    def center(self):
        return self._center

    """
      \ brief get the radius value
      \ return radius value
    """

    def radius(self):
        return self._radius

    """
        Line2D
      \ brief calculate the intersection with straight line
      \ param line considered line
      \ return the number of solution + solutions
        Ray2D
      \ brief calculate the intersection with ray line
      \ param ray considered ray
      \ return the number of solution + solutions
        Segment2D
      \ brief calculate the intersection with segment line
      \ param segment considered segment line
      \ return the number of solution + solutions
        Circle2D
      \ brief calculate the intersection with another circle
      \ param circle considered circle
      \ return the number of solution + solutions
    """

    def intersection(self,
                     line: Line2D = None,
                     ray: Ray2D = None,
                     segment: Segment2D = None,
                     circle=None):
        if line is not None:
            if math.fabs(line.a()) < EPSILON:
                if math.fabs(line.b()) < EPSILON:
                    return [0, Vector2D(), Vector2D()]

                n_sol = QUADRATIC_F(1.0,
                                    -2.0 * self._center._x,
                                    (SQUARE(self._center._x)
                                     + SQUARE(line.c() / line.b() + self._center._y)
                                     - SQUARE(self._radius)))
                x1 = n_sol[1]
                x2 = n_sol[2]
                if n_sol[0] > 0:
                    y1 = -line.c() / line.b()
                    sol_list = [n_sol[0], Vector2D(x1, y1), Vector2D(x2, y1)]
                else:
                    sol_list = [n_sol[0], Vector2D(), Vector2D()]
                return sol_list

            else:
                m = line.b() / line.a()
                d = line.c() / line.a()

                a = 1.0 + m * m
                b = 2.0 * (-self._center._y + (d + self._center._x) * m)
                c = (d + self._center._x) ** 2 + (self._center._y) ** 2 - (self._radius) ** 2

            n_sol = QUADRATIC_F(a, b, c)
            y1 = n_sol[1]
            y2 = n_sol[2]
            if n_sol[0] > 0:
                sol_list = [n_sol[0], Vector2D(line.getX(y1), y1), Vector2D(line.getX(y2), y2)]
            else:
                sol_list = [n_sol[0], Vector2D(), Vector2D()]

            return sol_list
        elif ray is not None:
            line_tmp = Line2D(origin=ray.origin(), angle=ray.dir())

            sol_list = self.intersection(line=line_tmp)
            if sol_list[0] > 1 and not ray.inRightDir(sol_list[2], 1.0):
                sol_list[0] -= 1

            if sol_list[0] > 0 and not ray.inRightDir(sol_list[1], 1.0):
                sol_list[1] = sol_list[2]
                sol_list[0] -= 1

            return sol_list

        elif segment is not None:
            line = segment.line()
            sol_list = self.intersection(line=line)
            if sol_list[0] > 1 and not segment.contains(sol_list[1]):
                sol_list[0] -= 1

            if sol_list[0] > 0 and not segment.contains(sol_list[2]):
                sol_list[0] -= 1

            return sol_list
        elif circle is not None:
            rel_x = circle.center()._x - self._center._x
            rel_y = circle.center()._y - self._center._y

            center_dist2 = rel_x * rel_x + rel_y * rel_y
            center_dist = math.sqrt(center_dist2)

            if center_dist < math.fabs(self._radius - circle.radius()) or self._radius + circle.radius() < center_dist:
                return [0, Vector2D(), Vector2D()]

            line = Line2D(a=-2.0 * rel_x, b=-2.0 * rel_y,
                          c=circle.center().r2() - circle.radius() * circle.radius() - self._center.r2() + self._radius * self._radius)

            return self.intersection(line=line)

    """  ----------------- static method  ----------------- """

    """
      \ brief get the circle through three points (circumcircle of the triangle).
      \ param p0 triangle's 1st vertex
      \ param p1 triangle's 2nd vertex
      \ param p2 triangle's 3rd vertex
      \ return coordinates of circumcenter
    """

    @staticmethod
    def circumcircle(p0, p1, p2):
        center = Triangle2D.tri_circumcenter(p0, p1, p2)

        if not center.is_valid():
            return Circle2D()

        return Circle2D(center, center.dist(p0))

    """
      \ brief check if the circumcircle contains the input point
      \ param point input point
      \ param p0 triangle's 1st vertex
      \ param p1 triangle's 2nd vertex
      \ param p2 triangle's 3rd vertex
      \ return True if circumcircle contains the point, False.
    """

    @staticmethod
    def circle_contains(point, p0, p1, p2):
        a = p1.x - p0.x
        b = p1.y - p0.y
        c = p2.x - p0.x
        d = p2.y - p0.y

        e = a * (p0.x + p1.x) + b * (p0.y + p1.y)
        f = c * (p0.x + p2.x) + d * (p0.y + p2.y)

        g = 2.0 * (a * (p2.y - p1.y) - b * (p2.x - p1.x))
        if math.fabs(g) < 1.0e-10:
            return False

        center = Vector2D((d * e - b * f) / g, (a * f - c * e) / g)
        return center.dist2(point) < center.dist2(p0) - EPSILON * EPSILON

    """
      \ brief make a logical print.
      \ return print_able str
    """

    def __repr__(self):
        return "({} , {})".format(self._center, self._radius)

    def to_str(self, ostr):
        ostr += ' (circle {} {} {})'.format(round(self.center().x(), 3), round(self.center().y(), 3), round(self.radius(), 3))


def test():
    c = Circle2D()
    print(c)


if __name__ == "__main__":
    test()
