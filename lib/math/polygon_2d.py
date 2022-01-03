"""
  \ file polygon_2d.py
  \ brief 2D polygon region File.
"""

from lib.math.rect_2d import Rect2D
from lib.math.region_2d import Region2D
from lib.math.vector_2d import Vector2D
from lib.math.angle_deg import AngleDeg
from lib.math.size_2d import Size2D
from lib.math.line_2d import Line2D
from lib.math.segment_2d import Segment2D
import math


class XLessEqual:
    def __init__(self, thr):
        self._thr = thr

    def operator(self, p: Vector2D):
        return p.x() <= self._thr

    def thr(self):
        return self._thr


class XMoreEqual:
    def __init__(self, thr):
        self._thr = thr

    def operator(self, p: Vector2D):
        return p.x() >= self._thr

    def thr(self):
        return self._thr


class YLessEqual:
    def __init__(self, thr):
        self._thr = thr

    def operator(self, p: Vector2D):
        return p.y() <= self._thr

    def thr(self):
        return self._thr


class YMoreEqual:
    def __init__(self, thr):
        self._thr = thr

    def operator(self, p: Vector2D):
        return p.y() >= self._thr

    def thr(self):
        return self._thr


class Polygon2D(Region2D):
    """
      \ brief create empty polygon
        List:
      \ brief create polygon with points
      \ param v array of points
    """

    def __init__(self, *args):  # , **kwargs):)
        super().__init__()
        if len(args) == 0:
            self._vertices = [Vector2D()]
        elif len(args[0]) > 0:
            self._vertices = args[0]
        else:
            self._vertices = [Vector2D()]

    """
      \ brief clear all data.
    """

    def clear(self):
        self._vertices = [Vector2D()]

    """
      \ brief set polygon with points
      \ param v array of points
      \ return  reference to itself
    """

    def assign(self, v):
        if len(v[0]) > 0:
            self._vertices = v

    """
      \ brief append point to polygon
      \ param p point
    """

    def addVertex(self, p: Vector2D):
        self._vertices.append(p)

    """
      \ brief get list of point of self polygon
      \ return  reference to point list
    """

    def vertices(self):
        return self._vertices

    """
      \ brief get bounding box of self polygon
      \ return bounding box of self polygon
    """

    def getBoundingBox(self):
        if len(self._vertices) == 0:
            return Rect2D()
        x_min = float("inf")
        x_max = - float("inf")
        y_min = float("inf")
        y_max = - float("inf")
        for p in self._vertices:
            if p.x() > x_max:
                x_max = p.x()

            if p.x() < x_min:
                x_min = p.x()

            if p.y() > y_max:
                y_max = p.y()

            if p.y() < y_min:
                y_min = p.y()
        return Rect2D(Vector2D(x_min, y_min), Size2D(x_max - x_min, y_max - y_min))

    """
      \ brief check point is in self polygon or not
      \ param p point for checking
      \ param allow_on_segment when point is on outline,
      if self parameter is set to True, True
      \ return True if point is in self polygon
    """

    def contains(self, p: Vector2D, allow_on_segment=True):
        if len(self._vertices) <= 0:
            return False
        elif len(self._vertices) == 1:
            return allow_on_segment and (self._vertices[0] == p)

        r = self.getBoundingBox()
        if not r.contains(p):
            return False

        #
        # make virtual half line
        #
        # print(r.right()) -> maxX
        line = Segment2D(p, Vector2D(p.x() + ((r.right() - r.left() + r.bottom() - r.top())
                                              + (self._vertices[0] - p).r()) * 3.0,
                                     p.y()))

        #
        # check intersection with all segments
        #
        inside = False
        min_line_x = r.right() + 1.0
        for i in range(len(self._vertices)):
            p1_index = i + 1

            if p1_index >= len(self._vertices):
                p1_index = 0

            p0 = self._vertices[i]
            p1 = self._vertices[p1_index]

            if not allow_on_segment:
                if Segment2D(p0, p1).onSegment(p):
                    return False

            if allow_on_segment and p == p0:
                return True

            if line.existIntersection(segment=Segment2D(p0, p1)):
                if p0.y() == p.y() or p1.y() == p.y():
                    if p0.y() == p.y():
                        if p0.x() < min_line_x:
                            min_line_x = p0.x()

                    if p1.y() == p.y():
                        if p1.x() < min_line_x:
                            min_line_x = p1.x()

                    if p0.y() == p1.y():
                        continue

                    elif p0.y() < p.y() or p1.y() < p.y():
                        continue

                inside = (not inside)

        return inside

    """
      \ brief get center of bounding box of self polygon
      \ return center of bounding box of self polygon
    """

    def xyCenter(self):
        return self.getBoundingBox().center()

    """
      \ brief get minimum distance between self polygon and point
      \ param p point
      \ param check_as_plane if self parameter is set to True, self
      polygon as a plane polygon,
      otherwise handle self polygon as a polyline polygon.
      when point is inside of self polygon, between plane polygon
      and point is 0,
      distance between polyline polygon and point is minimum distance
      between each segments of self polygon.
      \ return minimum distance between self polygon and point
    """

    def dist(self, p: Vector2D, check_as_plane=True):
        size = len(self._vertices)

        if size == 1:
            return (self._vertices[0] - p).r()

        if check_as_plane and self.contains(p):
            return 0.0

        min_dist = float("inf")
        for i in range(size - 1):

            seg = Segment2D(self._vertices[i],
                            self._vertices[i + 1])

            d = seg.dist(p)

            if d < min_dist:
                min_dist = d

        if size >= 3:
            seg = Segment2D(self._vertices[size - 1], self._vertices[0])

            d = seg.dist(p)

            if d < min_dist:
                min_dist = d

        return min_dist

    """
      \ brief get area of self polygon
      \ return value of area with sign.
    """

    def area(self):
        return math.fabs(self.doubleSignedArea() * 0.5)

    """
      \ brief calculate doubled signed area value
      \ return value of doubled signed area.
      If vertices are placed counterclockwise order, positive number.
      If vertices are placed clockwise order, negative number.
      Otherwise, 0.
    """

    def doubleSignedArea(self):
        size = len(self._vertices)
        ds_area_value = 0.0

        if size < 3:
            return ds_area_value

        for i in range(size):
            n = i + 1
            if n == size:
                n = 0
            ds_area_value += (
                    self._vertices[i].x() * self._vertices[n].y() - self._vertices[n].x() * self._vertices[i].y())

        return ds_area_value

    """
      \ brief check vertexes of self polygon is placed counterclockwise ot not
      \ return True if counterclockwise
    """

    def isCounterclockwise(self):
        return self.doubleSignedArea() > 0.0

    """
      \ brief check vertexes of self polygon is placed clockwise ot not
      \ return True if clockwise
    """

    def isClockwise(self):
        return self.doubleSignedArea() < 0.0

    """
      \ brief get a polygon clipped by a rectangle
      \ param r rectangle for clipping
      \ return a polygon. if polygon is separated by edges of rectangle,
      each separated polygon is connected to one polygon.
    """

    def getScissoredConnectedPolygon(self, r: Rect2D):
        if len(self._vertices) == 0:
            return Polygon2D()

        p = self._vertices
        clipped_p_1 = []
        clipped_p_2 = []
        clipped_p_3 = []
        clipped_p_4 = []
        clipped_p_1 = Polygon2D.scissorWithLine(XLessEqual(r.right()),
                                                p, clipped_p_1,
                                                Line2D(origin=Vector2D(r.maxX(), 0.0), angle=AngleDeg(90.0)))

        clipped_p_2 = Polygon2D.scissorWithLine(YLessEqual(r.bottom()),
                                                clipped_p_1, clipped_p_2,
                                                Line2D(origin=Vector2D(0.0, r.maxY()), angle=AngleDeg(0.0)))

        clipped_p_3 = Polygon2D.scissorWithLine(XMoreEqual(r.left()),
                                                clipped_p_2, clipped_p_3,
                                                Line2D(origin=Vector2D(r.minX(), 0.0), angle=AngleDeg(90.0)))

        clipped_p_4 = Polygon2D.scissorWithLine(YMoreEqual(r.top()),
                                                clipped_p_3, clipped_p_4,
                                                Line2D(origin=Vector2D(0.0, r.minY()), angle=AngleDeg(0.0)))

        return Polygon2D(clipped_p_4)

    @staticmethod
    def scissorWithLine(in_region, points, new_points, line):
        new_points.clear()

        in_rectangle = []
        for i in range(len(points)):
            in_rectangle.append(in_region(points[i]))
        for i in range(len(points)):
            index_0 = i
            index_1 = i + 1
            if index_1 >= len(points):
                index_1 = 0

            p0 = points[index_0]
            p1 = points[index_1]

            if in_rectangle[index_0]:
                if in_rectangle[index_1]:
                    new_points.append(p1)
                else:
                    c = line.intersection(line=Line2D(p1=p0, p2=p1))

                    if not c.is_valid():
                        return
                    new_points.push_back(c)
            else:
                if in_rectangle[index_1]:
                    c = line.intersection(line=Line2D(p1=p0, p2=p1))

                    if not c.is_valid():
                        return

                    new_points.push_back(c)
                    new_points.push_back(p1)
        return new_points

    """
      \ brief make a logical print.
      \ return print_able str
    """

    def __repr__(self):
        return "({})".format(self._vertices)


def test():
    p = Polygon2D([Vector2D(0, 0), Vector2D(0, 4), Vector2D(4, 4), Vector2D(4, 0)])
    v = [Vector2D(2, 2), Vector2D(5, 5)]
    print(p)
    print(p.isClockwise(), p.isCounterclockwise())
    print(p.doubleSignedArea(), p.area())
    print(p.getBoundingBox())
    print(p.contains(v[0]), p.contains(v[1]))


if __name__ == "__main__":
    test()
