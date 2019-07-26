from enum import Enum

from lib.math.angle_deg import AngleDeg
from lib.math.vector_2d import Vector2D


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
        self._self_pos: Vector2D = self_pos
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
