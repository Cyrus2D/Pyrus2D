"""
  \ file rect_2d.py
  \ brief 2D rectangle region File.
"""
from lib.math.size_2d import Size2D
from lib.math.segment_2d import Segment2D
from lib.math.region_2d import Region2D
from lib.math.ray_2d import Ray2D
from lib.math.vector_2d import Vector2D
from lib.math.angle_deg import AngleDeg
from lib.math.line_2d import Line2D
from lib.math.math_values import *
import math

"""
    The model and naming rules are depend on soccer simulator environment
          -34.0
            |
            |
-52.5 ------+------- 52.5
            |
            |
          34.0
"""


class Rect2D(Region2D):
    """
        4 num
      \ brief constructor
      \ param left_x left x
      \ param top_y top y
      \ param length length (x-range)
      \ param width width (y-range)
        Vector / 2 num
      \ brief constructor with variables
      \ param top_left top left point
      \ param length X range
      \ param width Y range
        Vector / Size
      \ brief constructor with variables
      \ param top_left top left point
      \ param size XY range
        2 Vector
      \ brief constructor with 2 points.
      \ param top_left top left vertex
      \ param bottom_right bottom right vertex

      Even if argument point has incorrect values,
      the assigned values are normalized automatically.
    """

    def __init__(self, *args):  # , **kwargs):)
        super().__init__()
        self._top_left = Vector2D()
        self._size = Size2D()
        self._is_valid = True
        if len(args) == 4:
            self._top_left = Vector2D(args[0], args[1])
            self._size = Size2D(args[2], args[3])
            self._is_valid = True
        elif len(args) == 3:
            self._top_left = args[0]
            self._size = Size2D(args[1], args[2])
            self._is_valid = True
        elif len(args) == 2 and type(args[1]) == Vector2D:
            self._top_left = args[0]
            bottom_right = args[1]
            top_left = args[0]
            self._size = Size2D(bottom_right.x - top_left.x, bottom_right.y - top_left.y)
            if bottom_right.x - top_left.x < 0.0:
                self._top_left._x = bottom_right.x

            if bottom_right.y - top_left.y < 0.0:
                self._top_left._y = bottom_right.y
                self._size = Size2D()
                self._is_valid = True
            else:
                self._top_left = Vector2D()
                self._size = Size2D()
                self._is_valid = True
        elif len(args) == 2:
            self._top_left = args[0]
            self._size = args[1]
            self._is_valid = True

    """
        4 NUM
      \ brief assign values
      \ param left_x left x
      \ param top_y top y
      \ param length X range
      \ param width Y range
        Vector / 2 NUM
      \ brief assign values
      \ param top_left top left point
      \ param length X range
      \ param width Y range
        Vector / Size
      \ brief assign values
      \ param top_left top left
      \ param size XY range
     """

    def assign(self, *args):  # , **kwargs):)
        super().__init__()
        if len(args) == 4:
            self._top_left.assign(args[0], args[1])
            self._size.assign(args[0], args[3])
        elif len(args) == 3:
            self._top_left = args[0]
            self._size.assign(args[1], args[2])
        elif len(args) == 2:
            self._top_left = args[0]
            self._size = args[1]

    """
      \ brief move the rectangle.
      the center point is set to the given position.
      the size is unchanged.
      \ param point center coordinates
    """

    def moveCenter(self, point):
        self._top_left.assign(point.x - self._size.length() * 0.5, point.y - self._size.width() * 0.5)

    """
      \ brief move the rectangle.
      the top-left corner is set to the given position.
      the size is unchanged.
      \ param point top-left corner
    """

    def moveTopLeft(self, point):
        self._top_left = point

    """
      \ brief move the rectangle.
      the bottom-right corner is set to the given position.
      the size is unchanged.
      \ param point bottom-right corner
    """

    def moveBottomRight(self, point):
        self._top_left.assign(point.x - self._size.length(), point.y - self._size.width())

    """
      \ brief move the rectangle.
      the left line is set to the given position.
      the size is unchanged.
      \ param x left value
    """

    def moveLeft(self, x):
        self._top_left._x = x

    """
      \ brief alias of moveLeft.
      \ param x left value
    """

    def moveMinX(self, x):
        self.moveLeft(x)

    """
      \ brief move the rectangle.
      the right line is set to the given value.
      the size is unchanged.
      \ param x right value
    """

    def moveRight(self, x):
        self._top_left._x = x - self._size.length()

    """
      \ brief alias of moveRight.
      \ param x right value
    """

    def moveMaxX(self, x):
        self.moveRight(x)

    """
      \ brief move the rectangle.
      the top line is set to the given value.
      the size is unchanged.
      \ param y top value
    """

    def moveTop(self, y):
        self._top_left._y = y

    """
      \ brief alias of moveTop.
      \ param y top value
    """

    def moveMinY(self, y):
        self.moveTop(y)

    """
      \ brief move the rectangle.
      the top line is set to the given value.
      the size is unchanged.
      \ param y top value
    """

    def moveBottom(self, y):
        self._top_left._y = y - self._size.width()

    """
      \ brief alias of moveTop.
      \ param y top value
    """

    def moveMaxY(self, y):
        self.moveBottom(y)

    """
        2 Num
      \ brief set the top-left corner of the rectangle.
      \ param x x coordinate
      \ param y y coordinate
        Vector
      \ brief set the top-left corner of the rectangle.
      \ param point coordinate
      the size may be changed, the bottom-right corner will never be changed.
    """

    def setTopLeft(self, *args):
        x = 0.0
        y = 0.0
        if len(args) == 1:
            x = args[0].x()
            y = args[0].y()
        elif len(args) == 2:
            x = args[0]
            y = args[1]
        new_left = min(self.right(), x)
        new_right = max(self.right(), x)
        new_top = min(self.bottom(), y)
        new_bottom = max(self.bottom(), y)
        return self.assign(new_left, new_top, new_right - new_left, new_bottom - new_top)

    """
        2 Num
      \ brief set the bottom-right corner of the rectangle.
      \ param x x coordinate
      \ param y y coordinate
        Vector
      \ brief set the bottom-right corner of the rectangle.
      \ param point coordinate
        the size may be changed, the top-left corner will never be changed.
    """

    def setBottomRight(self, *args):
        x = 0.0
        y = 0.0
        if len(args) == 1:
            x = args[0].x()
            y = args[0].y()
        elif len(args) == 2:
            x = args[0]
            y = args[1]
        new_left = min(self.left(), x)
        new_right = max(self.left(), x)
        new_top = min(self.top(), y)
        new_bottom = max(self.top(), y)
        return self.assign(new_left, new_top, new_right - new_left, new_bottom - new_top)

    """
      \ brief set the left of rectangle.
      the size may be changed, the right will never be changed.
      \ param x left value
     """

    def setLeft(self, x):
        new_left = min(self.right(), x)
        new_right = max(self.right(), x)
        self._top_left._x = new_left
        self._size.setLength(new_right - new_left)

    """
      \ brief alias of setLeft.
      \ param x left value
     """

    def setMinX(self, x):
        self.setLeft(x)

    """
      \ brief set the right of rectangle.
      the size may be changed, the left will never be changed.
      \ param x right value 
    """

    def setRight(self, x):
        new_left = min(self.left(), x)
        new_right = max(self.left(), x)

        self._top_left._x = new_left
        self._size.setLength(new_right - new_left)

    """
      \ brief alias of setRight.
      \ param x right value
    """

    def setMaxX(self, x):
        self.setRight(x)

    """
      \ brief set the top of rectangle.
      the size may be changed, the bottom will never be changed.
      \ param y top value
    """

    def setTop(self, y):
        new_top = min(self.bottom(), y)
        new_bottom = max(self.bottom(), y)

        self._top_left._y = new_top
        self._size.setWidth(new_bottom - new_top)

    """
      \ brief alias of setTop.
      \ param y top value
    """

    def setMinY(self, y):
        self.setTop(y)

    """
      \ brief set the bottom of rectangle.
      the size may be changed, the top will never be changed.
      \ param y bottom value
    """

    def setBottom(self, y):
        new_top = min(self.top(), y)
        new_bottom = max(self.top(), y)

        self._top_left._y = new_top
        self._size.setWidth(new_bottom - new_top)

    """
      \ brief alias of setBottom.
      \ param y top value
    """

    def setMaxY(self, y):
        self.setBottom(y)

    """
      \ brief set a x-range
      \ param length range
    """

    def setLength(self, length):
        self._size.setLength(length)

    """
      \ brief set a y-range
      \ param width range
    """

    def setWidth(self, width):
        self._size.setWidth(width)

    """
        2 NUM
      \ brief set a size
      \ param length range
      \ param width range
       1 Size
      \ brief set a size
      \ param size range
    """

    def setSize(self, *args):  # , **kwargs):)
        if len(args) == 2:
            self._size.assign(args[0], args[1])
        elif len(args) == 1:
            self._size = args[0]

    """
      \ brief check if self rectangle is valid or not.
      \ return True if the area of self rectangle is not 0.
    """

    def isValid(self):
        return self._size.isValid()

    """
      \ brief get the area value of self rectangle.
      \ return value of the area
    """

    def area(self):
        return self._size.length() * self._size.width()

    """
      \ brief check if point is within self region.
      \ param point considered point
      \ return True or False
    """

    def contains(self, point: Vector2D):
        return self.left() <= point.x() <= self.right() and self.top() <= point.y() <= self.bottom()

    """
      \ brief check if point is within self region with error threshold.
      \ param point considered point
      \ param error_thr error threshold
      \ return True or False
    """

    def containsWeakly(self, point, error_thr):
        return self.left() - error_thr <= point.x <= self.right() + error_thr and self.top() - error_thr <= point.y <= self.bottom() + error_thr

    """
      \ brief get the left x coordinate of self rectangle.
      \ return x coordinate value
    """

    def left(self):
        return self._top_left.x()

    """
      \ brief get the right x coordinate of self rectangle.
      \ return x coordinate value
    """

    def right(self):
        return self.left() + self._size.length()

    """
      \ brief get the top y coordinate of self rectangle.
      \ return y coordinate value
    """

    def top(self):
        return self._top_left.y()

    """
      \ brief get the bottom y coordinate of self rectangle.
      \ return y coordinate value
    """

    def bottom(self):
        return self.top() + self._size.width()

    """
      \ brief get minimum value of x coordinate of self rectangle
      \ return x coordinate value (equivalent to left())
    """

    # TODO minX / minY / maxX / minX
    def minX(self):
        self.left()

    """
      \ brief get maximum value of x coordinate of self rectangle
      \ return x coordinate value (equivalent to right())
    """

    def maxX(self):
        self.right()

    """
      \ brief get minimum value of y coordinate of self rectangle
      \ return y coordinate value (equivalent to top())
    """

    def minY(self):
        self.top()

    """
      \ brief get maximum value of y coordinate of self rectangle
      \ return y coordinate value (equivalent to bottom())
    """

    def maxY(self):
        self.bottom()

    """
      \ brief get the XY range of self rectangle
      \ return size object
    """

    def size(self):
        return self._size

    """
      \ brief get center point
      \ return coordinate value by vector object
     """

    def center(self):
        return Vector2D((self.left() + self.right()) * 0.5,
                        (self.top() + self.bottom()) * 0.5)

    """
      \ brief get the top-left corner point
      \ return coordinate value by vector object
    """

    def topLeft(self):
        return self._top_left

    """
      \ brief get the top-right corner point
      \ return coordinate value by vector object
    """

    def topRight(self):
        return Vector2D(self.right(), self.top())

    """
      \ brief get the bottom-left corner point
      \ return coordinate value by vector object
    """

    def bottomLeft(self):
        return Vector2D(self.left(), self.bottom())

    """
      \ brief get the bottom-right corner point
      \ return coordinate value by vector object
    """

    def bottomRight(self):
        return Vector2D(self.right(), self.bottom())

    """
      \ brief get the left edge line
      \ return line object
    """

    def leftEdge(self):
        return Line2D(p1=self.topLeft(), p2=self.bottomLeft())

    """
      \ brief get the right edge line
      \ return line object
    """

    def rightEdge(self):
        return Line2D(p1=self.topRight(), p2=self.bottomRight())

    """
      \ brief get the top edge line
      \ return line object
    """

    def topEdge(self):
        return Line2D(p1=self.topLeft(), p2=self.topRight())

    """
      \ brief get the bottom edge line
      \ return line object
    """

    def bottomEdge(self):
        return Line2D(p1=self.bottomLeft(), p2=self.bottomRight())

    """
        Line2D
      \ brief calculate intersection point with line.
      \ param line considered line.
      \ param sol1 pointer to the 1st solution variable
      \ param sol2 pointer to the 2nd solution variable
      \ return number of intersection
        Ray2D
      \ brief calculate intersection point with ray.
      \ param ray considered ray line.
      \ param sol1 pointer to the 1st solution variable
      \ param sol2 pointer to the 2nd solution variable
      \ return number of intersection
        Segment2D
      \ brief calculate intersection point with line segment.
      \ param segment considered line segment.
      \ param sol1 pointer to the 1st solution variable
      \ param sol2 pointer to the 2nd solution variable
      \ return number of intersection
    """

    def intersection(self,
                     line: Line2D = None,
                     ray: Ray2D = None,
                     segment: Segment2D = None):  # , **kwargs):):
        if line is not None:
            n_sol = 0
            t_sol = [Vector2D(0, 0), Vector2D(0, 0)]
            left_x = self.left()
            right_x = self.right()
            top_y = self.top()
            bottom_y = self.bottom()

            t_sol[n_sol] = self.leftEdge().intersection(line)

            if n_sol < 2 and t_sol[n_sol].is_valid() and top_y <= t_sol[n_sol].y() <= bottom_y:
                n_sol += 1

            t_sol[n_sol] = self.rightEdge().intersection(line)

            if n_sol < 2 and t_sol[n_sol].is_valid() and top_y <= t_sol[n_sol].y() <= bottom_y:
                n_sol += 1

            t_sol[n_sol] = self.topEdge().intersection(line)

            if n_sol < 2 and (t_sol[n_sol]).is_valid() and left_x <= t_sol[n_sol].x() <= right_x:
                n_sol += 1

            t_sol[n_sol] = self.topEdge().intersection(line)

            if n_sol < 2 and (t_sol[n_sol]).is_valid() and left_x <= t_sol[n_sol].x() <= right_x:
                n_sol += 1

            if n_sol == 2 and math.fabs(t_sol[0].x() - t_sol[1].x()) < EPSILON and math.fabs(
                    t_sol[0].y() - t_sol[1].y()) < EPSILON:
                n_sol = 1

            sol_list = [n_sol, t_sol[0], t_sol[1]]

            return sol_list

        elif ray is not None:
            n_sol = self.intersection(line=ray.line())

            if n_sol[0] > 1 and not ray.inRightDir(n_sol[2], 1.0):
                n_sol[0] -= 1

            if n_sol[0] > 0 and not ray.inRightDir(n_sol[1], 1.0):
                n_sol[1] = n_sol[2]
                n_sol[0] -= 1

            return n_sol
        elif segment is not None:
            n_sol = self.intersection(line=segment.line())
            if n_sol[0] > 1 and not segment.contains(n_sol[2]):
                n_sol[0] -= 1

            if n_sol[0] > 0 and not segment.contains(n_sol[1]):
                n_sol[1] = n_sol[2]
                n_sol[0] -= 1

            return n_sol

    """
     \ brief get the intersected rectangle of self rectangle and the other rectangle.
     If no intersection between rectangles,empty rectangle is returned.
     \ param other other rectangle
     \ return rectangle instance.
    """

    def intersected(self, other):
        if not self.isValid or not other.is_valid():
            self._top_left.assign(0.0, 0.0)
            self._size.assign(0.0, 0.0)

        left = max(self.left(), other.left())
        top = max(self.top(), other.top())
        w = min(self.right(), other.right()) - left
        h = min(self.bottom(), other.bottom()) - top

        if w <= 0.0 or h <= 0.0:
            self._top_left.assign(0.0, 0.0)
            self._size.assign(0.0, 0.0)

        self._top_left.assign(left, top)
        self._size.assign(w, h)

    """
      \ brief get the united rectangle of self rectangle and the other rectangle.
      \ param other other rectangle
      \ return rectangle instance.
    """

    def united(self, other):
        if not self.isValid or not other.is_valid():
            self._top_left.assign(0.0, 0.0)
        self._size.assign(0.0, 0.0)

        left = max(self.left(), other.left())
        top = max(self.top(), other.top())
        w = min(self.right(), other.right()) - left
        h = min(self.bottom(), other.bottom()) - top

        if w <= 0.0 or h <= 0.0:
            self._top_left.assign(0.0, 0.0)
            self._size.assign(0.0, 0.0)

        self._top_left.assign(left, top)
        self._size.assign(w, h)

    """  ----------------- static method  ----------------- """

    """
        4 NUM
      \ brief create rectangle with center point and size.
      \ param center_x x value of center point of rectangle.
      \ param center_y y value of center point of rectangle.
      \ param length length(x-range) of rectangle.
      \ param width width(y-range) of rectangle.
    """

    @staticmethod
    def from_center(*args):  # , **kwargs):)
        if len(args) == 4:
            return Rect2D(args[0] - args[2] * 0.5, args[1] - args[3] * 0.5, args[2], args[3])
        elif len(args) == 3:
            return Rect2D(args[0] - args[2] * 0.5, args[1] - args[3] * 0.5)

    """
      \ brief create rectangle with 2 corner points. just call one of constructor.
    """

    @staticmethod
    def from_corners(*args):  # , **kwargs):)
        return Rect2D(args)

    """
      \ brief make a logical print.
      \ return print_able str
    """

    def __repr__(self):
        return "[len:{},wid:{}]".format(self._top_left, self._size)

    def to_str(self, ostr):
        ostr += ' (rect {} {} {} {})'.format(round(self.left(), 3), round(self.top(), 3),
                                             round(self.right(), 3), round(self.bottom(), 3))


def test():
    origin = Vector2D(0, 0)
    terminal = Vector2D(10, 10)
    seg = Segment2D(origin, terminal)
    print(seg)
    seg.assign(1.0, 2.0, 3, 4)
    print(seg)
    seg.assign(origin, 10, AngleDeg(53.1301023541559835905))
    print(seg)


if __name__ == "__main__":
    test()
