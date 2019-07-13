import math

EPSILON = 1.0e-5
ERROR_VALUE = 1e20
DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi


class AngleDeg:
    def __init__(self):
        self._degree = 0

    def __init__(self, __degree):
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

    def degree(self):
        return self._degree

    def abs(self):
        return math.fabs(self.degree())

    def radian(self):
        return self.degree() * DEG2RAD

    def __iadd__(self, other):
        if type(other) == AngleDeg:
            self._degree += other.degree()
        else:
            self._degree += other
        self.normal()

    def __isub__(self, other):
        if type(other) == AngleDeg:
            self._degree -= other.degree()
        else:
            self._degree -= other
        self.normal()

    def __imul__(self, other):
        self._degree *= other
        self.normal()

    def __idiv__(self, other):
        self._degree /= other
        self.normal()

    def __add__(self, other):
        if type(other) == AngleDeg:
            new_angle_deg = AngleDeg(self._degree + other.degree())
        else:
            new_angle_deg = AngleDeg(self._degree + other)
        return new_angle_deg

    def __isub__(self, other):
        if type(other) == AngleDeg:
            new_angle_deg = AngleDeg(self._degree + other.degree())
        else:
            new_angle_deg = AngleDeg(self._degree + other)
        return new_angle_deg

    def __imul__(self, other):
        new_angle_deg = AngleDeg(self._degree * other)
        return new_angle_deg

    def __idiv__(self, other):
        new_angle_deg = AngleDeg(self._degree / other)
        return new_angle_deg

    def __repr__(self):
        return str(self.degree())

    def cos(self):
        return math.cos(self.degree() * DEG2RAD)

    def sin(self):
        return math.sin(self.degree() * DEG2RAD)

    def tan(self):
        return math.tan(self.degree() * DEG2RAD)

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
            AngleDeg.rad2deg(math.asin(sine))

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


if __name__ == "__main__":
    test()
