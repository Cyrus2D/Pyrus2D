from enum import Enum

from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.vector_2d import Vector2D


class InterceptInfo:
    class Mode(Enum):
        NORMAL = 0
        EXHAUST = 100

    def __init__(self, mode: Mode = Mode.EXHAUST, turn_cycle: int = 10000, dash_cycle: int = 10000,
                 dash_power: float = 100000, dash_angle: float = 0,
                 self_pos: Vector2D = Vector2D(-10000, 0), ball_dist: float = 100000, stamina: float = 0):
        self._valid: bool = True
        self._mode: InterceptInfo.Mode = mode
        self._turn_cycle: int = turn_cycle
        self._dash_cycle: int = dash_cycle
        self._dash_power: float = dash_power
        self._dash_angle: AngleDeg = AngleDeg(dash_angle)
        self._self_pos: Vector2D = self_pos.copy()  # object in object then copy
        self._ball_dist: float = ball_dist
        self._stamina: float = stamina
        if self._mode == InterceptInfo.Mode.EXHAUST and \
                self._turn_cycle == 10000 and \
                self._dash_cycle == 10000 and \
                self._dash_power == 100000.0 and \
                self._dash_angle == AngleDeg(0.0) and \
                self._self_pos == Vector2D(-10000.0, 0.0) and \
                self._ball_dist == 10000000.0 and \
                self._stamina == 0.0:
            self._valid = False

    def init(self, mode: Mode = Mode.EXHAUST, turn_cycle: int = 10000, dash_cycle: int = 10000,
             dash_power: float = 100000, dash_angle: float = 0,
             self_pos: Vector2D = Vector2D(-10000, 0), ball_dist: float = 100000, stamina: float = 0):
        self.__init__(mode, turn_cycle, dash_cycle, dash_power, dash_angle, self_pos, ball_dist, stamina)

    def is_valid(self):
        return self._valid

    def mode(self):
        return self._mode

    def turn_cycle(self):
        return self._turn_cycle

    def dash_cycle(self):
        return self._dash_cycle

    def reach_cycle(self):
        return self._dash_cycle + self._turn_cycle

    def dash_power(self):
        return self._dash_power

    def dash_angle(self):
        return self._dash_angle

    def self_pos(self):
        return self._self_pos

    def ball_dist(self):
        return self._ball_dist

    def stamina(self):
        return self._stamina

    @staticmethod
    def compare(lhs, rhs):
        return True if lhs.reach_cycle() < rhs.reach_cycle() else (
                lhs.reach_cycle() == rhs.reach_cycle() and lhs.turn_cycle() < rhs.turn_cycle())

    def __lt__(self, other):
        if self.reach_cycle() < other.reach_cycle():
            return True
        return self.reach_cycle() == other.reach_cycle() and self.turn_cycle() < other.turn_cycle()

    def __repr__(self):
        return (f"(mode: {self._mode},"
                f"each_cycle: {self.reach_cycle()},"
                f"turn_cycle: {self._turn_cycle},"
                f"dash_cycle: {self._dash_cycle},"
                f"dash_power: {self._dash_power},"
                f"dash_angle: {self._dash_angle.degree()},"
                f"self_pos: {self._self_pos},"
                f"ball_dist: {self._ball_dist},"
                f"stamina: {self._stamina})")
