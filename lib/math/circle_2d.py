"""
  \ file circle_2d.py
  \ brief 2D circle region File.
"""

from lib.math.triangle_2d import *

"""
  \brief solve quadratic fomula
  \param a fomula constant A
  \param b fomula constant B
  \param c fomula constant C
  \param sol1 reference to the result variable
  \param sol2 reference to the result variable
  \ return number of solution
 """


def QUADRATIC_F(a, b, c, sol1, sol2):
    d = b * b - 4.0 * a * c
    # ignore small noise
    if math.fabs(d) < EPSILON:
        sol1 = -b / (2.0 * a)
        return 1

    elif d < 0.0:
        return 0

    else:
        d = math.sqrt(d)
        sol1 = (-b + d) / (2.0 * a)
        sol2 = (-b - d) / (2.0 * a)
        return 2


def SQUARE(v):
    return v * v


class Circle2D:
    """
        Default:
      \ brief create a zero area circle at (0,0)
        Len = 2
      \ brief construct with center point and radius value.
      \ param c center point
      \ param r radius value
    """

    def __init__(self, *args):  # , **kwargs):)
        if len(args) == 2 and isinstance(args[0], Vector2D):
            self.center = args[0]
            self.radius = args[1]
            if args[1] < 0.0:
                self.radius = 0.0
            self.is_valid = True
        else:
            self.center = Vector2D()
            self.radius = 0.0
            self.is_valid = True

    """
      \ brief assign value.
      \ param c center point
      \ param r radius value
    """

    def assign(self, c: Vector2D, r: float):
        self.center = c
        self.radius = r
        if r < 0.0:
            self.radius = 0.0

    """
      \ brief get the area value of self circle
      \ return value of the area
     """

    def area(self):
        return PI * self.radius * self.radius

    """
      \ brief check if point is within self region
      \ param point considered point
      \ return True if point is contained by self circle
     """

    def contains(self, point: Vector2D):
        return self.center.dist2(point) < self.radius * self.radius

    """
      \ brief get the center point
      \ return center point coordinate value
     """

    def center(self):
        return self.center

    """
      \ brief get the radius value
      \ return radius value
    """

    def radius(self):
        return self.radius

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

    def intersection(self, *args):  # , **kwargs):):):
        if len(args) == 1 and isinstance(args[0], Line2D):
            line = args[0]
            if math.fabs(line.a()) < EPSILON:
                if math.fabs(line.b()) < EPSILON:
                    return 0

                x1 = 0.0
                x2 = 0.0
                n_sol = QUADRATIC_F(1.0,
                                    -2.0 * self.center.x,
                                    (SQUARE(self.center.x)
                                     + SQUARE(line.c() / line.b() + self.center.y)
                                     - SQUARE(self.radius)),
                                    x1,
                                    x2)

                if n_sol > 0:
                    y1 = -line.c() / line.b()
                    sol_list = [n_sol, Vector2D(x1, y1), Vector2D(x2, y1)]
                else:
                    sol_list = [n_sol]
                return sol_list

            else:
                m = line.b() / line.a()
                d = line.c() / line.a()

                a = 1.0 + m * m
                b = 2.0 * (-self.center.y + (d + self.center.x) * m)
                c = SQUARE(d + self.center.x) + SQUARE(self.center.y) - SQUARE(self.radius)

            y1 = 0.0
            y2 = 0.0
            n_sol = QUADRATIC_F(a, b, c, y1, y2)

            sol_list = [n_sol, Vector2D(line.getX(y1), y1), Vector2D(line.getX(y2), y2)]
            return sol_list
        elif len(args) == 1 and isinstance(args[0], Ray2D):
            ray = args[0]
            tsol1 = Vector2D(0, 0)
            tsol2 = Vector2D(0, 0)
            line_tmp = Line2D(ray.origin(), ray.dir())

            n_sol = Circle2D.intersection(line_tmp)  # TODO Check LineTMP

            if n_sol[0] > 1 and not ray.inRightDir(tsol2, 1.0):
                n_sol[0] -= 1

            if n_sol[0] > 0 and not ray.inRightDir(tsol1, 1.0):
                tsol1 = tsol2
                n_sol[0] -= 1

            sol_list = [n_sol[0], tsol1, tsol2]

            return sol_list

        elif len(args) == 1 and (args[0], Segment2D):
            seg = args[0]
            line = seg.line()
            tsol1 = Vector2D()
            tsol2 = Vector2D()

            n_sol = Circle2D.intersection(line)

            if n_sol[0] > 1 and not seg.contains(tsol2):
                n_sol[0] -= 1

            if n_sol > 0 and not seg.contains(tsol1):
                n_sol[0] -= 1

            sol_list = [n_sol[0], tsol1, tsol2]

            return sol_list

        elif len(args) == 1 and isinstance(args[0], Circle2D):
            circle = args[0]

            rel_x = circle.center().x - self.center.x
            rel_y = circle.center().y - self.center.y

            center_dist2 = rel_x * rel_x + rel_y * rel_y
            center_dist = math.sqrt(center_dist2)

            if center_dist < math.fabs(self.radius - circle.radius()) or self.radius + circle.radius() < center_dist:
                return

            line = Line2D(-2.0 * rel_x, -2.0 * rel_y,
                          circle.center().r2() - circle.radius() * circle.radius() - self.center.r2() + self.radius * self.radius)

            return self.intersection(line)

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
        center = Triangle2D.Scircumcenter(p0, p1, p2)

        if not center.isValid():
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
    def Scontains(point, p0, p1, p2):
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
        return "({} , {})".format(self.center, self.radius)


def test():
    c = Circle2D()
    print(c)


if __name__ == "__main__":
    test()
