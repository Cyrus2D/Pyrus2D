from lib.math.angledeg import *


class Vector2D:
    def __init__(self, __x=0, __y=0):
        self.x = __x
        self.y = __y
        self.is_valid = True

    def assign(self, __x, __y):
        self.__init__(__x, __y)
        return self

    def set_polar(self, __r, __d):
        if type(__d) is not AngleDeg:
            __d = AngleDeg(__d)
        self.x = __r * __d.cos()
        self.y = __r * __d.sin()

    def invalidate(self):
        self.is_valid = False

    def isvalid(self):
        return self.is_valid

    def r(self):
        return self.x * self.x + self.y + self.y

    def lenght(self):
        return self.r()

    def th(self):
        return AngleDeg(AngleDeg.atan2_deg(self.y, self.x))

    def dir(self):
        return self.th()

    def absX(self):
        return math.fabs(self.x)

    def absY(self):
        return math.fabs(self.y)

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def add(self, _x, _y):
        self.x += _x
        self.y += _y

    def scale(self, scaler):
        self.x *= scaler
        self.y *= scaler

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __imul__(self, other):
        self.x *= other
        self.y *= other

    def __idiv__(self, other):
        self.x /= other
        self.y /= other

    def dist(self, other):
        return math.sqrt(math.pow(self.x - other.x, 2) + math.pow(self.y - other.y, 2))

    def reverse(self):
        self.x *= (-1.0)
        self.y *= (-1.0)

    def reverse_vector(self):
        new_vector = Vector2D(self.x, self.y)
        new_vector.reverse()
        return new_vector

    def set_length(self, len):
        mag = self.r()
        if mag > EPSILON:
            self.scale(len / mag);

    def set_lenght_vector(self, len):
        new_vector = Vector2D(self.x, self.y)
        new_vector.set_length(len)
        return new_vector

    def normalize(self):
        self.set_length(1)

    def normalize_vetor(self):
        new_vector = Vector2D(self.x, self.y)
        new_vector.set_length(1)
        return new_vector

    def rotate(self, deg):
        if type(deg) == AngleDeg:
            self.rotate(deg.degree())
        c = math.cos(deg * DEG2RAD)
        s = math.sin(deg * DEG2RAD)
        self.assign(self.x * c - self.y * s,self.x * s + self.y * c )

    def rotate_vector(self, deg):
        new_vector = Vector2D(self.x, self.y)
        return new_vector.rotate(deg)

    def set_dir(self, dir):
        radius = self.r()
        self.x = radius * dir.cos()
        self.y = radius * dir.sin()

    @staticmethod
    def polar2vector(__r, __d):
        new_vector = Vector2D()
        new_vector.set_polar(__r, __d)

    def __repr__(self):
        return "({},{})".format(self.x, self.y)



a = Vector2D(1,1)
b = Vector2D(10,10)
a.set_length(10)
print(a)
c = (a + b)
print(c)
a.set_polar(10, 45)
print(c.th())