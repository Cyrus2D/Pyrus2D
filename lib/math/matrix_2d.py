"""
    \ file matrix_2d.py
    \ brief 2D transform matrix class File.

    ( m11, m12, dx )
    ( m21, m22, dy )
    (   0,   0,  1 )


     self.11 /element (1,1): the horizontal scaling factor.
     self.12  element (1,2): the vertical shearing factor.
     self.21  element (2,1): the horizontal shearing factor.
     self.22 element (2,2): the vertical scaling factor.
     self.dx  dx: the horizontal translation factor.
     self.dy  dy: the vertical translation factor.

"""

from lib.math.vector_2d import Vector2D
from lib.math.angle_deg import AngleDeg
import math

class Matrix2D:
    """
      \ brief create a matrix with all elements OR create an identity matrix
      \ param __11 the horizontal scaling factor.
      \ param __12 the vertical shearing factor.
      \ param __21 the horizontal shearing factor.
      \ param __22 the vertical scaling factor.
      \ param __x the horizontal translation factor.
      \ param __y the vertical translation factor.
    """

    def __init__(self, __11=1.0, __12=0.0, __21=0.0, __22=1.0, __x=0.0, __y=0.0):
        self._m11 = __11
        self._m12 = __12
        self._m21 = __21
        self._m22 = __22
        self._dx = __x
        self._dy = __y
        self.is_valid = True

    """
      \ brief reset to the identity matrix
    """

    def reset(self):
        self._m11 = self._m22 = 1.0
        self._m12 = self._m21 = self._dx = self._dy = 0.0

    """
      \ brief set a matrix element with the specified values.
      \ param __11 the horizontal scaling factor.
      \ param __12 the vertical shearing factor.
      \ param __21 the horizontal shearing factor.
      \ param __22 the vertical scaling factor.
      \ param __x the horizontal translation factor.
      \ param __y the vertical translation factor.
    """

    def assign(self, __11, __12, __21, __22, __x, __y):
        self._m11 = __11
        self._m12 = __12
        self._m21 = __21
        self._m22 = __22
        self._dx = __x
        self._dy = __y

    """
      \ brief accessor : get the horizontal scaling factor.
      \ return the horizontal scaling factor value.
    """

    def m11(self):
        return self._m11

    """
      \ brief accessor : get the vertical shearing factor.
      \ return the vertical shearing factor value.
    """

    def m12(self):
        return self._m12

    """
      \ brief accessor : get the horizontal shearing factor.
      \ return the horizontal shearing factor value.
    """

    def m21(self):
        return self._m21

    """
      \ brief accessor : get the vertical scaling factor.
      \ return the vertical scaling factor value.
    """

    def m22(self):
        return self._m22

    """
      \ brief accessor : get the horizontal translation factor.
      \ return the horizontal translation factor value.
    """

    def dx(self):
        return self._dx

    """
      \ brief accessor : get the vertical translation factor.
      \ return the vertical translation factor value.
    """

    def dy(self):
        return self._dy

    """ 
     \ brief get the matrix's determinant
     \ return the determinant value.
    """

    def det(self):
        return self._m11 * self._m22 - self._m12 * self._m21

    """
      \ brief check if this matrix is invertible (is not insular).
      \ return true if this matrix is invertible.
    """

    def invertible(self):
        return math.fabs(self.det()) > 0.00000000001

    """
      \ brief get the inverted matrix.
      \ return the inverted matrix object.
    """

    def inverted(self):
        determinant = self.det()
        if determinant == 0.0:  # never invertible
            return Matrix2D()  # default matrix

        dinv = 1.0 / determinant
        return Matrix2D(self._m22 * dinv, -self._m12 * dinv,
                        -self._m21 * dinv, self._m11 * dinv,
                        (self._m12 * self._dy - self._dx * self._m22) * dinv,
                        (self._dx * self._m21 - self._m11 * self._dy) * dinv)

    """
      \ brief moves the coordinate as the other matrix.
      \ param dx move factor for the x axis.
      \ param dy move factor for the y axis.
      
      same as :
        self = Matrix2D.make_translation(dx,dy) * self
      
    """

    def translate(self, dx, dy):
        self._dx += dx
        self._dy += dy

    """
      \ brief scales the coordinate systeother.
      \ param sx scaling factor for the x axis.
      \ param sy scaling factor for the y axis.

      same as:
        self = Matrix2D.make_scaling(sx,sy) * self        
    """

    def scale(self, sx, sy):
        self._m11 *= sx
        self._m12 *= sx
        self._dx *= sx
        self._m21 *= sy
        self._m22 *= sy
        self._dy *= sy

    """
      \ brief rotates the coordinate system
      \ param angle rotation angle
      
      same as:
        self = Matrix2D.make_rotation(angle) * self
    """

    def rotate(self, angle: AngleDeg):
        ang_sin = angle.sin()
        ang_cos = angle.cos()
        tm11 = self._m11 * ang_cos - self._m21 * ang_sin
        tm12 = self._m12 * ang_cos - self._m22 * ang_sin
        tm21 = self._m11 * ang_sin + self._m21 * ang_cos
        tm22 = self._m12 * ang_sin + self._m22 * ang_cos
        tdx = self._dx * ang_cos - self._dy * ang_sin
        tdy = self._dx * ang_sin + self._dy * ang_cos

        self._m11 = tm11
        self._m12 = tm12
        self._dx = tdx
        self._m21 = tm21
        self._m22 = tm22
        self._dy = tdy

    """
        Len = 1 / Vector2D
      \ brief create transformed vector from input vector with this matrix
      \ param v input vector
      \ return mapped vector object
        Len = 2 / XY
      \ brief create transformed vector from input coordinates with this matrix
      \ param x input x-coordinates value
      \ param y input y-coordinates value
      \ return mapped vector object
    """

    def transform(self, *args):  # **kwargs):
        if len(args) == 1:
            v = args[0]
            return Vector2D(self._m11 * v.x + self._m12 * v.y + self._dx,
                            self._m21 * v.x + self._m22 * v.y + self._dy)
        if len(args) == 2:
            return Vector2D(self._m11 * args[0] + self._m12 * args[1] + self._dx,
                            self._m21 * args[0] + self._m22 * args[1] + self._dy)

    """
      \ brief transform input vector with this matrix
      \ param v input vector
    """

    def transform_vec(self, v: Vector2D):
        tx = self._m11 * v.x() + self._m12 * v.y() + self._dx
        ty = self._m21 * v.x() + self._m22 * v.y() + self._dy
        v.assign(tx, ty)

    """  ----------------- static method  ----------------- """

    """
      \ brief create the translation matrix.
      \ param dx the horizontal translation factor.
      \ param dy the vertical translation factor.
      \ return new matrix object  
    """

    @staticmethod
    def make_translation(dx, dy):
        return Matrix2D(1.0, 0.0, 0.0, 1.0, dx, dy)

    """
      \ brief create the scaling matrix.
      \ param sx the horizontal scaling factor.
      \ param sy the vertical scaling factor.
      \ return new matrix object
    """

    @staticmethod
    def make_scaling(sx, sy):
        return Matrix2D(sx, 0.0, 0.0, sy, 0.0, 0.0)

    """
      \ brief create the rotation matrix.
      \ param angle the rotation angle
      \ return new matrix object
    """

    @staticmethod
    def make_rotation(angle: AngleDeg):
        ang_cos = angle.cos()
        ang_sin = angle.sin()
        return Matrix2D(ang_cos, -ang_sin, ang_sin, ang_cos, 0.0, 0.0)

    """ ----------------- operators section  ----------------- """

    """
      \ brief multiplied by other matrix
      \ param other left hand side matrix
    """

    def __imul__(self, other):
        tm11 = self._m11 * other.m11() + self._m12 * other.m21()
        tm12 = self._m11 * other.m12() + self._m12 * other.m22()
        tm21 = self._m21 * other.m11() + self._m22 * other.m21()
        tm22 = self._m21 * other.m12() + self._m22 * other.m22()
        tdx = self._m11 * other.dx() + self._m12 * other.dcy() + self._dx
        tdy = self._m21 * other.dx() + self._m22 * other.dy() + self._dy

        self._m11 = tm11
        self._m12 = tm12
        self._m21 = tm21
        self._m22 = tm22
        self._dx = tdx
        self._dy = tdy

    """
        Len = 1 / Matrix2D
     \ brief multiplication operator of Matrix x Matrix.
     \ param lhs left hand side matrix.
     \ param rhs right hand side matrix
     \ return result matrix object
        Len = 1 / Vector2D
     \ brief multiplication(transformation) operator of Matrix x Vector.
     \ param lhs left hand side matrix.
     \ param rhs right hand side vector
     \ return result vector object
    """

    def __mul__(self, *args):  # , **kwargs):):
        if len(args) == 1 and type(args[0]) == Vector2D:
            return self.transform(args[0])
        if len(args) == 1:
            mat_tmp = self
            return mat_tmp.__imul__(args[0])

    """
      \ brief make a logical print.
      \ return print_able str
    """

    def __repr__(self):
        return "{ [ " + str(self._m11) + " ] , [ " + str(self._m12) + " ] , [ " + str(self._dx) + " ]\n  [ " + str(
            self._m21) + " ] , [ " + str(self._m22) + " ] , [ " + str(self._dy) + " ] }"


def test():
    a = Matrix2D()
    print(a)


if __name__ == "__main__":
    test()
