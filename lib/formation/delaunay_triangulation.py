from scipy.spatial import Delaunay
from pyrusgeom.geom_2d import *
from enum import Enum
from lib.rcsc.server_param import ServerParam
from pyrusgeom.soccer_math import min_max

class FormationType(Enum):
    Static = 's'
    DelaunayTriangulation2 = 'D'


class Formation:
    def __init__(self, path):
        self._balls = []
        self._players = []
        self._triangles = []
        self._formation_type = FormationType.Static
        self._target_players = []
        self._path = path
        self.read_file(path)
        self.calculate()

    def read_file(self, path):
        file = open(path, 'r')
        lines = file.readlines()
        if lines[0].find('Static') < 0:
            self._formation_type = FormationType.DelaunayTriangulation2
        if self._formation_type == FormationType.Static:
            self.read_static(lines)
        else:
            self.read_delaunay(lines)

    def read_static(self, lines):
        for i in range(len(lines)):
            if i == 0 or lines[i].startswith('#'):
                continue
            player = lines[i].split()
            self._target_players.append(Vector2D(float(player[2]), float(player[3])))

    def read_delaunay(self, lines):
        for i in range(len(lines)):
            if lines[i].find('Ball') >= 0:
                self.read_sample(i, lines)
            i += 11

    def read_sample(self, i, lines):
        ball = lines[i].split(' ')
        ball_x = float(ball[1])
        ball_y = float(ball[2])
        self._balls.append([ball_x, ball_y])
        players = []
        for j in range(1, 12):
            player = lines[i + j].split(' ')
            player_x = float(player[1])
            player_y = float(player[2])
            players.append([player_x, player_y])
        self._players.append(players)

    def calculate(self):
        if self._formation_type == FormationType.Static:
            return
        self._tri = Delaunay(self._balls).simplices
        for tri in self._tri:
            tmp = [Triangle2D(Vector2D(self._balls[tri[0]][0], self._balls[tri[0]][1]),
                                    Vector2D(self._balls[tri[1]][0], self._balls[tri[1]][1]),
                                    Vector2D(self._balls[tri[2]][0], self._balls[tri[2]][1])), tri[0], tri[1], tri[2]]
            self._triangles.append(tmp)

    def update(self, B:Vector2D):
        SP = ServerParam.i()
        if self._formation_type == FormationType.Static:
            return
        ids = []
        
        point = B.copy()
        if point.abs_x() > SP.pitch_half_length():
            point._x = min_max(-SP.pitch_half_length(), point.x(), +SP.pitch_half_length())
        if point.abs_y() > SP.pitch_half_width():
            point._y = min_max(-SP.pitch_half_width(), point.y(), +SP.pitch_half_width())
        
        for tri in self._triangles:
            if tri[0].contains(point):
                ids = [tri[1], tri[2], tri[3]]
                break
        Pa = Vector2D(self._balls[ids[0]][0], self._balls[ids[0]][1])
        Pb = Vector2D(self._balls[ids[1]][0], self._balls[ids[1]][1])
        Pc = Vector2D(self._balls[ids[2]][0], self._balls[ids[2]][1])
        lineProj = Line2D(p1=Pb, p2=Pc).projection(B)
        m1 = Pb.dist(lineProj)
        n1 = Pc.dist(lineProj)
        m2 = Pa.dist(B)
        n2 = lineProj.dist(B)

        self._target_players.clear()
        for p in range(11):
            OPa = Vector2D(self._players[ids[0]][p][0], self._players[ids[0]][p][1])
            OPb = Vector2D(self._players[ids[1]][p][0], self._players[ids[1]][p][1])
            OPc = Vector2D(self._players[ids[2]][p][0], self._players[ids[2]][p][1])
            OI = (OPc - OPb)
            OI *= (m1 / (m1 + n1))
            OI += OPb
            OB = (OI - OPa)
            OB *= (m2 / (m2 + n2))
            OB += OPa
            self._target_players.append(OB)

    def get_pos(self, unum):
        return self._target_players[unum - 1]

    def get_poses(self):
        return self._target_players

    def __repr__(self):
        return self._path

# f = Formation('base/formations-dt/before-kick-off.conf')
# debug_print(len(f._balls))
# debug_print(len(f._players))
# debug_print(f._formation_type)
# f.update(Vector2D(20, 16))
# debug_print(f._formation_type)
# debug_print(f._target_players)
