"""
  \ file vector_2d.py
  \ brief 2d vector class
"""

from lib.math.angle_deg import AngleDeg
from lib.math.math_values import *
import math


class Vector2D:  # TODO maybe give some bugs because of x and _x and x()
    """
       \ brief default constructor : create Vector with XY value directly.
       \ param __x assigned x value
       \ param __y assigned x value
    """

    def __init__(self,
                 x: float = None,
                 y: float = None,
                 vector2d=None):
        if x is not None and y is not None:
            self._x = x
            self._y = y
        elif vector2d is not None:
            self._x = vector2d._x
            self._y = vector2d._y
        else:
            self._x = 0
            self._y = 0
        self._is_valid = True

    """
        \ brief assign XY value directly.
        \ param __x assigned x value
        \ param __y assigned y value
        \ return reference to itself
    """

    def assign(self, __x, __y):
        self._x = __x
        self._y = __y
        return self

    """
     \ brief accessor
     \ return X coordinate
    """

    def x(self):
        return self._x

    """
      \ brief accessor
      \ return Y coordinate
    """

    def y(self):
        return self._y

    """
      \ brief assign XY value from POLAR value.
      \ param __r vector's radius
      \ param __d vector's angle
     """

    def set_polar(self, __r, __d):
        if type(__d) is not AngleDeg:
            __d = AngleDeg(__d)
        self._x = __r * __d.cos()
        self._y = __r * __d.sin()

    """
      \ brief invalidate this object     
    """

    def invalidate(self):
        self._is_valid = False

    """
      \ brief check is the object valid
      \ return is_valid     
    """

    def is_valid(self):
        return self._is_valid

    """
      \ brief get the squared length of vector.
      \ return squared length value
    """

    def r2(self):
        return self._x * self._x + self._y * self._y

    """
      \ brief get the length of vector.
      \ return length value
    """

    def r(self):
        return math.sqrt(self.r2())

    """
      \ brief get the length of vector. this method is equivalent to r().
      \ return length value 
    """

    def length(self):
        return self.r()

    """
      \ brief get the squared length of vector. this method is equivalent to r2().
      \ return squared length value
    """

    def length2(self):
        return self.r2()

    """
      \ brief get the angle of vector.
      \ return angle
    """

    def th(self):
        return AngleDeg(AngleDeg.atan2_deg(self._y, self._x))

    """
      \ brief get the angle of vector. this method is equivalent to th().
      \ return angle
     """

    def dir(self):
        return self.th()

    """
      \ brief get new vector that XY values were set to absolute value.
      \ return new vector that all values are absolute.
    """

    def abs(self):
        return Vector2D(abs(self._x), abs(self._y))

    """
      \ brief get absolute x value
      \ return absolute x value
    """

    def absX(self):
        return math.fabs(self._x)

    """
      \ brief get absolute y value
      \ return absolute y value
    """

    def absY(self):
        return math.fabs(self._y)

    """
        Len = 1 / Vector2D
      \ brief add vector.
      \ param other added vector
        Len = 2 / XY
      \ brief add XY values respectively.
      \ param _x added x value
      \ param _y added y value
    """

    def add(self, *args):  # **kwargs):
        if len(args) == 1:
            self._x += args[0].x()
            self._y += args[0].y()
        elif len(args) == 2:
            self._x += args[0]
            self._y += args[1]

    """
      \ brief scale this vector
      \ param scalar scaling factor
    """

    def scale(self, scalar):
        self._x *= scalar
        self._y *= scalar

    """  __ operator section __"""

    def __add__(self, other):
        return Vector2D(self._x + other.x(), self._y + other.y())

    def __sub__(self, other):
        return Vector2D(self._x - other._x, self._y - other._y)

    def __truediv__(self, other):
        return Vector2D(self._x / other, self._y / other)

    def __mul__(self, other):
        return Vector2D(self._x * other, self._y * other)

    def __iadd__(self, other):
        self._x += other.x()
        self._y += other.y()
        return self

    def __isub__(self, other):
        self._x -= other.x()
        self._y -= other.y()
        return self

    def __imul__(self, other):
        self._x *= other
        self._y *= other
        return self

    def __idiv__(self, other):
        self._x /= other
        self._y /= other
        return self

    def add_x(self, x: float):
        self._x += x

    def add_y(self, y: float):
        self._y += y

    def sub_x(self, x: float):
        self._x -= x

    def sub_y(self, y: float):
        self._y -= y

    """
      \ brief get the squared distance from this to 'other'.
      \ param other target point
      \ return squared distance to 'other'
    """

    def dist2(self, other):
        return math.pow(self._x - other.x(), 2) + math.pow(self._y - other.y(), 2)

    """
      \ brief get the distance from this to 'p'.
      \ param p target point
      \ return distance to 'p'
    """

    def dist(self, other):
        return math.sqrt(self.dist2(other))

    """
      \ brief reverse vector components
    """

    def reverse(self):
        self._x *= (-1.0)
        self._y *= (-1.0)

    """
      \ brief get reversed vector.
      \ return new vector object
    """

    def reverse_vector(self):
        new_vector = Vector2D(self._x, self._y)
        new_vector.reverse()
        return new_vector

    """
      \ brief set vector length to 'length'.
      \ param len new length to be set
    """

    def set_length(self, length):
        mag = self.r()
        if mag > EPSILON:
            self.scale(length / mag)

    """
      \ brief get new vector that the length is set to 'length'
      \ param len new length to be set
      \ return new vector that the length is set to 'length'
    """

    def set_length_vector(self, length):
        new_vector = Vector2D(self._x, self._y)
        new_vector.set_length(length)
        return new_vector

    """
      \ brief normalize vector. length is set to 1.0.
    """

    def normalize(self):
        self.set_length(1)

    """
      \ brief get new normalized vector that the length is set to 1.0 with the same angle as self
      \ return new normalized vector
    """

    def normalize_vector(self):
        new_vector = Vector2D(self._x, self._y)
        new_vector.set_length(1)
        return new_vector

    """
      \ brief get inner(dot) product with 'v'.
      \ param v target vector
      \ return value of inner product
    """

    def innerProduct(self, v):
        return self._x * v.x() + self._y * v.y()
        # ==  |this| * |v| * (*this - v).th().cos()

    """
      \ brief get virtual outer(cross) product with 'v'.
      \ param v target vector
      \ return value of outer product
    """

    def outerProduct(self, v):
        #   xn = self.y * v.z - self.z * v.y;
        #   yn = self.z * v.x - self.x * v.z;
        #   zn = self.x * v.y - self.y * v.x;
        return self._x * v._y - self._y * v._x
        # == |this| * |v| * (*this - v).th().sin()

    """
      \ brief check if this vector is strictly same as given vector.
      \ param other compared vector
      \ return true if strictly same, otherwise false.
    """

    def equals(self, other):
        return self._x == other.x() and self._y == other.y()

    """
      \ brief check if this vector is weakly same as given vector.
      \ param other compared vector.
      \ return true if weakly same, otherwise false.
    """

    def equalsWeakly(self, other):
        return math.fabs(self._x - other.x) < EPSILON and math.fabs(self._y - other.y) < EPSILON

    """
      \ brief rotate this vector with 'deg'
      \ param deg rotated angle by double type
    """

    def rotate(self, deg):
        if type(deg) == AngleDeg:
            self.rotate(deg.degree())
            return self
        cos_tmp = math.cos(deg * DEG2RAD)
        sin_tmp = math.sin(deg * DEG2RAD)
        self.assign(self._x * cos_tmp - self._y * sin_tmp, self._x * sin_tmp + self._y * cos_tmp)
        return self

    """
      \ brief get new vector that is rotated by 'deg'.
      \ param deg rotated angle. double type.
      \ return new vector rotated by 'deg'
    """

    def rotated_vector(self, deg):
        new_vector = Vector2D(self._x, self._y)
        return new_vector.rotate(deg)

    """
      \ brief set vector's angle to 'angle'
      \ param direction new angle to be set
      \ return reference to itself
    """

    def set_dir(self, direction):
        radius = self.r()
        self._x = radius * direction.cos()
        self._y = radius * direction.sin()

    """
      \ brief make an invalid vector2D
      \ return invalid vector2D   
    """

    @staticmethod
    def invalid():
        vec_invalid = Vector2D()
        vec_invalid.invalidate()
        return vec_invalid

    """
      \ brief get new Vector created by POLAR value.
      \ param mag length of vector
      \ param theta angle of vector
      \ return new vector object
    """

    @staticmethod
    def from_polar(mag, theta):
        return Vector2D(mag * theta.cos(), mag * theta.sin())

    """
      \ brief get new Vector created by POLAR value.
      \ param mag length of vector
      \ param theta angle of vector
      \ return new vector object
    """

    @staticmethod
    def polar2vector(__r, __d):
        new_vector = Vector2D()
        new_vector.set_polar(__r, __d)
        return new_vector

    """
      \ brief get inner(dot) product for v1 and v2.
      \ param v1 input 1
      \ param v2 input 2
      \ return value of inner product
    """

    @staticmethod
    def inner_product(v1, v2):
        return v1.innerProduct(v2)

    """
      \ brief get outer(cross) product for v1 and v2.
      \ param v1 input 1
      \ param v2 input 2
      \ return value of outer product
    """

    @staticmethod
    def outer_product(v1, v2):
        return v1.outerProduct(v2)

    """
      \ brief make a logical print.
      \ return print_able str
    """

    def __repr__(self):
        return "({},{})".format(self._x, self._y)

    def copy(self):
        return Vector2D(self._x, self._y)


def test():
    a = Vector2D(1, 1)
    b = Vector2D(10, 10)
    a.set_length(10)
    print(a)
    c = (a + b)
    print(c)
    a.set_polar(10, AngleDeg(45))
    print(c.th())


if __name__ == "__main__":
    test()
