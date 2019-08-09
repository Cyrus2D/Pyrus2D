import math

EPSILON = 1.0e-6
ERROR_VALUE = 1e20
DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi
PI = 3.14159265358979323846


class AngleDeg:
    PI = 3.14159265358979323846

    def __init__(self, __degree=0.0):
        if isinstance(__degree,  AngleDeg):
            __degree = __degree.degree()
        self._degree = __degree
        self.normal()

    def normal(self):
        if self._degree < -360.0 or 360.0 < self._degree:
            self._degree = math.fmod(self._degree, 360.0)

        if self._degree < -180.0:
            self._degree += 360.0

        if self._degree > 180.0:
            self._degree -= 360.0

    def __eq__(self, other):
        if type(other) == AngleDeg:
            self._degree = other.degree()
        else:
            self._degree = other
            self.normal()

    def isWithin(self, left, right):
        if left.isLeftEqualOf(right):
            if left.isLeftEqualOf(self) and self.isLeftEqualOf(right):
                return True
        else:
            if self.isLeftEqualOf(right) or left.isLeftEqualOf(self):
                return True
        return False

    def isLeftEqualOf(self, angle):
        diff = angle.degree() - self._degree
        return 0.0 <= diff < 180.0 or diff < -180.0

    def degree(self):
        return self._degree

    def set_degree(self, degree: float):
        self.__init__(degree)

    def abs(self):
        return math.fabs(self.degree())

    def radian(self):
        return self.degree() * DEG2RAD

    def reverse(self):
        if self._degree >= 0:
            self._degree = -(180 - self._degree)  # Aref eh zeshte :)) # 3 saat debug budam saresh :/ # btw code che gonahi karde?
        else:
            self._degree = 180 + self._degree
        return self._degree

    def __iadd__(self, other):
        if type(other) == AngleDeg:
            self._degree += other.degree()
        else:
            self._degree += other
        self.normal()
        return self

    def __isub__(self, other):
        if type(other) == AngleDeg:
            self._degree -= other.degree()
        else:
            self._degree -= other
        self.normal()
        return self

    def __imul__(self, other):
        self._degree *= other
        self.normal()
        return self

    def __idiv__(self, other):
        self._degree /= other
        self.normal()
        return self

    def __add__(self, other):
        if type(other) == AngleDeg:
            new_angle_deg = AngleDeg(self._degree + other.degree())
        else:
            new_angle_deg = AngleDeg(self._degree + other)
        return new_angle_deg

    def __sub__(self, other):
        if isinstance(other, AngleDeg):
            new_angle_deg = AngleDeg(self._degree - other.degree())
        else:
            new_angle_deg = AngleDeg(self._degree - other)
        return new_angle_deg

    def __mul__(self, other):
        new_angle_deg = AngleDeg(self._degree * other)
        return new_angle_deg

    def __floordiv__(self, other):
        new_angle_deg = AngleDeg(self._degree / other)
        return new_angle_deg

    def __repr__(self):
        return str(self.degree())

    def __float__(self):
        return self.degree()

    def __neg__(self):
        new_angle_deg = AngleDeg(-self._degree)
        return new_angle_deg

    def cos(self):
        return math.cos(self.degree() * DEG2RAD)

    def sin(self):
        return math.sin(self.degree() * DEG2RAD)

    def tan(self):
        return math.tan(self.degree() * DEG2RAD)

    def is_left_of(self, angle):
        diff = angle.degree() - self.degree()
        return (0.0 < diff and diff < 180.0 ) or diff < -180.0

    def is_right_of(self, angle):
        diff = self.degree() - angle.degree()
        return (0.0 < diff and diff < 180.0) or diff < -180.0

    @staticmethod
    def rad2deg(rad):
        return rad * RAD2DEG

    @staticmethod
    def deg2rad(deg):
        return deg * DEG2RAD

    @staticmethod
    def cos_deg(deg):
        return math.cos(AngleDeg.deg2rad(deg))

    @staticmethod
    def sin_deg(deg):
        return math.sin(AngleDeg.deg2rad(deg))

    @staticmethod
    def tan_deg(deg):
        return math.tan(AngleDeg.deg2rad(deg))

    @staticmethod
    def acos_deg(cosine):
        if cosine >= 1.0:
            return 0.0
        elif cosine <= -1.0:
            return 180.0
        else:
            AngleDeg.rad2deg(math.acos(cosine))

    @staticmethod
    def asin_deg(sine):
        if sine >= 1.0:
            return 90.0
        elif sine <= -1.0:
            return -90.0
        else:
            return AngleDeg.rad2deg(math.asin(sine))

    @staticmethod
    def atan_deg(tangent):
        return AngleDeg.rad2deg(math.atan(tangent))

    @staticmethod
    def atan2_deg(y, x):
        if x is 0.0 and y is 0.0:
            return 0.0
        else:
            return AngleDeg.rad2deg(math.atan2(y, x))

    @staticmethod
    def bisect(left, right):
        result = AngleDeg(left)
        rel = AngleDeg(right - left)
        diff = result.degree() - AngleDeg(right).degree()
        half_deg = rel.degree() * 0.5
        result += half_deg
        if (0.0 < diff < 180.0) or diff < -180.0:
            return result
        return result + 180.0


def test():
    a = AngleDeg(30)
    b = AngleDeg(60)
    print(a + b)
    c = (a + b)
    print(c.sin())
    print(c.tan())

    print(AngleDeg.atan2_deg(10, 5))

    x = AngleDeg(-10)
    y = (-x)
    print(y)
    print(-x)

if __name__ == "__main__":
    test()
