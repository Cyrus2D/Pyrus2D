"""
  \ file size_2d.py
  \ brief 2d size class  File.
"""

import math


class Size2D:
    """
     \ brief constructor with variables
     \ param length x range
     \ param width y range
        Default 0.0 0.0
    """

    def __init__(self, __l=0.0, __w=0.0):
        self._length = math.fabs(__l)
        self._width = math.fabs(__w)

    """
      \ brief assign range directly.
      \ param length X range
      \ param width Y range
    """

    def assign(self, length, width):
        self._length = math.fabs(length)
        self._width = math.fabs(width)

    """
      \ brief set X range
      \ param length X range
    """

    def setLength(self, length):
        self._length = math.fabs(length)

    """
      \ brief set Y range
      \ param width Y range
      \ return reference to itself
    """

    def setWidth(self, width):
        self._width = math.fabs(width)

    """
      \ brief get the value of X range
      \ return value of X range
     """

    def length(self):
        return self._length

    """
      \ brief get the value of Y range
      \ return value of Y range
     """

    def width(self):
        return self._width

    """
      \ brief get the length of diagonal line
      \ return length of diagonal line
     """

    def diagonal(self):
        return math.sqrt(self._length * self._length + self._width * self._width)

    """
      \ brief check if size is valid or not.
      \ return True if the area of self rectangle is not 0.
     """

    def isValid(self):
        return self._length > 0.0 and self._width > 0.0

    """
      \ brief make a logical print.
      \ return print_able str
    """

    def __repr__(self):
        return "[len:{},wid:{}]".format(self._length, self._width)
