"""
  \ file convex_hull.py
  \ brief 2D convex hull File.
"""

from enum import Enum, unique, auto
import functools

from lib.math.triangle_2d import Triangle2D
from lib.math.polygon_2d import Polygon2D
from lib.math.vector_2d import Vector2D
from lib.math.segment_2d import Segment2D
from math_values import *


"""
  \ enum MethodType
  \ brief algorithm type
 """


@unique
class MethodType(Enum):
    DirectMethod = auto()
    WrappingMethod = auto()
    GrahamScan = auto()


"""
  \ brief function to get unique values 
  \ param list1 one list
  \ return unique_list
 """


def unique(list1):
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


# Base for AngleSortPredicate
BASE_ = Vector2D()


def AngleSortPredicate(item1, item2):
    # check if "base_ - lhs - rhs" is clockwise order or not.

    area = Triangle2D.double_signed_area(BASE_, item1, item2)

    if area < 0.0:
        return -1

    if area < EPSILON:
        if BASE_._y < item1.y:
            if BASE_.dist2(item1) > BASE_.dist2(item2):
                return -1

        else:
            if BASE_.dist2(item1) < BASE_.dist2(item2):
                return -1

    return 1


def is_clockwise(p0, p1, p2):
    area = Triangle2D.double_signed_area(p0, p1, p2)

    return area < 0.0 or (area < EPSILON and p0.dist2(p1) > p0.dist2(p2))


class ConvexHull:
    """
        \ brief create empty convex hull
         OR
        \ brief create convex hull with given points
        \ param v array of input points
    """

    def __init__(self, v: list):
        self._input_points = v  # not < input points
        self._vertices = []  # not < vertices of convex hull, by counter clockwise order
        self._edges = []  # not < edges of convex hull (should be ordered by counter clockwise?)

    """
      \ brief clear all data.
    """

    def clear(self):
        self.clearResults()
        self._input_points.clear()

    """
      \ brief clear result variables.
     """

    def clearResults(self):
        self._vertices.clear()
        self._edges.clear()

    """
      \ brief add a point to the set of input point
      \ param p point
    """

    def addPoint(self, p):
        self._input_points.append(p)

    """
      \ brief add points to the set of input point
      \ param v input point container
    """

    def addPoints(self, v):
        for p in v:
            self._input_points.append(p)

    """
      \ brief generate convex hull by specified method
      \ param type method type id
    """

    def compute(self, M_type=MethodType.WrappingMethod):
        if M_type == MethodType.DirectMethod:
            self.computeDirectMethod()
        elif M_type == MethodType.GrahamScan:
            self.computeGrahamScan()
        elif M_type == MethodType.WrappingMethod:
            self.computeWrappingMethod()

    """
      \ brief get the reference to the input point container
      \ return  reference to the input point container
    """

    def inputPoints(self):
        return self._input_points

    """
      \ brief get the reference to the vertex container ordered by counter clockwise
      \ return  reference to the ordered vertex container
    """

    def vertices(self):
        return self._vertices

    """
      \ brief get the reference to the result edge container
      \ return  reference to the result edge container
    """

    def edges(self):
        return self._edges

    """
      \ brief direct method version
    """

    def computeDirectMethod(self):
        self.clearResults()

        point_size = len(self._input_points)

        if point_size < 3:
            return

        for i in range(point_size - 1):
            p = self._input_points[i]
            for j in range(i + 1, point_size):
                q = self._input_points[j]
                rel = q - p

                valid = True
                last_value = 0.0

                for k in range(point_size):
                    if k == i or k == j:
                        continue

                    r = self._input_points[k]
                    outer_prod = rel.outerProduct(r - p)

                    if math.fabs(outer_prod) < EPSILON:
                        # point is on the line
                        if (r - p).r2() < rel.r2():
                            # point is on the segment
                            valid = False
                            break

                    if (outer_prod > 0.0 and last_value < 0.0) or (outer_prod < 0.0 and last_value > 0.0):
                        # point exists in the opposite side
                        valid = False
                        break

                    last_value = outer_prod

                if valid:
                    self._vertices.append(p)
                    self._vertices.append(q)

                    if last_value < 0.0:
                        self._edges.append(Segment2D(p, q))

                    else:
                        self._edges.append(Segment2D(q, p))

        # sort vertices by counter clockwise order

        if len(self._vertices):
            BASE_ = self._vertices[len(self._vertices) - 1]
            self._vertices.sort(key=functools.cmp_to_key(AngleSortPredicate))
            self._vertices = unique(self._vertices)

    """
     \ brief wrapping method version
    """

    def computeWrappingMethod(self):
        self.clearResults()

        point_size = len(self._input_points)

        if point_size < 3:
            return

        min_index = self.getMinPointIndex()

        if min_index == -1:
            return

        vertices = []  # temporal set for checking already used vertices.

        self._vertices.append(self._input_points[min_index])

        current_index = min_index
        current_point = self._input_points[min_index]
        for loop_count in range(point_size + 1):
            candidate = 0
            for i in range(point_size):
                if i == current_index:
                    continue
                if vertices.index(i) != len(self._vertices) - 1:
                    continue
                candidate = i
                break
            for i in range(candidate + 1, point_size):
                if i == current_index:
                    continue
                if vertices.index(i) != len(self._vertices) - 1:
                    continue

                p = self._input_points[candidate]
                q = self._input_points[i]

                area = Triangle2D.double_signed_area(current_point, p, q)

                if area < 0.0:
                    candidate = i

                elif area < EPSILON:
                    if current_point.dist2(p) > current_point.dist2(q):
                        candidate = i
            current_index = candidate
            current_point = self._input_points[current_index]
            vertices.append(current_index)
            self._vertices.append(current_point)

            if current_index == min_index:
                break

        for p in self._vertices:
            if p != self._vertices[-1]:
                self._edges.append(Segment2D(p, p + 1))

        self._vertices.pop()

    """
      \ brief Graham scan method version
    """

    def computeGrahamScan(self):
        self.clearResults()

        point_size = len(self._input_points)

        if point_size < 3:
            return

        min_index = self.getMinPointIndex()

        if min_index == -1:
            return

        self.sortPointsByAngleFrom(min_index)

        self._vertices = self._input_points

        top = 1
        for i in range(2, point_size):
            while is_clockwise(self._vertices[top - 1], self._vertices[top], self._input_points[i]):
                top -= 1

            top += 1
            tmp = self._vertices[top]
            self._vertices[top] = self._vertices[i]
            self._vertices[i] = tmp

        top += 1

        del self._vertices.remove[top:len(self._vertices)]

        for p in self._vertices:
            if p != self._vertices[-1]:
                self._edges.append(Segment2D(p, p + 1))
        self._edges.append(Segment2D(self._vertices[0], self._vertices[-1]))

    """
      \ brief get the index of minimum coordinate point
    """

    def getMinPointIndex(self):
        point_size = len(self._input_points)

        if point_size == 0:
            return -1

        min_index = 0

        min_point = self._input_points[0]
        for i in range(point_size):
            p = self._input_points[i]

            if min_point.x > p.x or (min_point.x == p.x and min_point.y > p.y):
                min_point = p
                min_index = i

        return min_index

    def sortPointsByAngleFrom(self, index):
        if len(self._input_points) <= index:
            return

        tmp = self._input_points[0]
        self._input_points[0] = self._input_points[index]
        self._input_points[index] = tmp

        self._input_points.sort(key=functools.cmp_to_key(AngleSortPredicate))

    """
      \ brief get the convex hull polygon
      \ return 2d polygon object
    """

    def toPolygon(self):
        return Polygon2D(self._vertices)

    """
      \ brief make a logical print.
      \ return print_able str
    """

    def __repr__(self):
        return "({} , {})".format(self._vertices, self._edges)


def test():
    v = [Vector2D(), Vector2D(1, 1), Vector2D(0, 1)]
    c = ConvexHull(v)
    print(c)


if __name__ == "__main__":
    test()
