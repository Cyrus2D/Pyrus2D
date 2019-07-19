"""
  \ file polygon_2d.h
  \ brief 2D polygon region File.
"""

from lib.math.rect_2d import *
from lib.math.region_2d import *


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
        elif isinstance(args[0][0], Vector2D):
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
        if isinstance(v[0], Vector2D):
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
        if len(self._vertices):
            return Rect2D()
        x_min = float("inf")
        x_max = - float("inf")
        y_min = float("inf")
        y_max = - float("inf")
        for p in self._vertices:
            if p.x > x_max:
                x_max = p.x

            if p.x < x_min:
                x_min = p.x

            if p.y > y_max:
                y_max = p.y

            if p.y < y_min:
                y_min = p.y
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
        line = Segment2D(p, Vector2D(p.x + ((r.maxX() - r.minX()
                                             + r.maxY() - r.minY())
                                            + (self._vertices[0] - p).r()) * 3.0,
                                     p.y))

        #
        # check intersection with all segments
        #
        inside = False
        min_line_x = r.maxX() + 1.0
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

            if line.existIntersection(Segment2D(p0, p1)):
                if p0.y == p.y or p1.y == p.y:
                    if p0.y == p.y:
                        if p0.x < min_line_x:
                            min_line_x = p0.x

                    if p1.y == p.y:
                        if p1.x < min_line_x:
                            min_line_x = p1.x

                    if p0.y == p1.y:
                        continue

                    elif p0.y < p.y or p1.y < p.y:
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
            ds_area_value += (self._vertices[i].x * self._vertices[n].y - self._vertices[n].x * self._vertices[i].y)

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

    #    def getScissoredConnectedPolygon(self, r: Rect2D):

    """
      \ brief make a logical print.
      \ return print_able str
    """

    def __repr__(self):
        return "({})".format(self._vertices)


def test():
    p = Polygon2D([Vector2D(0, 2), Vector2D(0, 4), Vector2D(0, 0), Vector2D(3, 0)])
    v = [Vector2D(1, 1), Vector2D(5, 5)]
    print(p)
    print(p.isClockwise(), p.isCounterclockwise())
    print(p.doubleSignedArea(), p.area())
    print(p.contains(v[0]), p.contains(v[1]))  # TODO Check Contains


if __name__ == "__main__":
    test()
