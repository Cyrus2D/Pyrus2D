from enum import Enum, unique, auto

from lib.math.angle_deg import AngleDeg
from lib.math.vector_2d import Vector2D


class TrainerCommand:
    @unique
    class Type(Enum):
        INIT = auto()  # connection command

        CHECK_BALL = auto()
        LOOK = auto()
        TEAM_NAMES = auto()

        EAR = auto()
        EYE = auto()

        START = auto()
        CHANGE_MODE = auto()
        MOVE = auto()
        RECOVER = auto()
        CHANGE_PLAYER_TYPE = auto()
        SAY = auto()

        COMPRESSION = auto()
        DONE = auto()

        ILLEGAL = auto()

    def __init__(self):
        pass

    def type(self):
        pass

    def str(self):
        pass


class TrainerTeamNameCommand(TrainerCommand):
    def __init__(self):
        super().__init__()

    def type(self):
        return TrainerCommand.Type.TEAM_NAMES

    def str(self):
        return "(team_name)"


class TrainerSendCommands(TrainerCommand):
    @staticmethod
    def all_to_str(commands):
        commands_msg = ""
        for command in commands:
            commands_msg += command.str()  # TODO FIX THIS
        commands_msg = commands_msg
        return commands_msg


class TrainerMoveBallCommand(TrainerCommand):
    def __init__(self, pos: Vector2D, vel: Vector2D = None):
        super().__init__()
        self._pos = pos
        self._vel = vel

    def type(self):
        return TrainerCommand.Type.MOVE

    def str(self):
        if self._vel is None:
            return f"(move (ball) {self._pos.x()} {self._pos.y()})"
        return f"(move (ball) {self._pos.x()} {self._pos.y()}" \
               f" 0 {self._vel.x()} {self._vel.y()})"


class TrainerMovePlayerCommand(TrainerCommand):
    def __init__(self,
                 teamname: str,
                 unum: int,
                 pos: Vector2D,
                 angle: float = None,
                 vel: Vector2D = None):
        super().__init__()
        self._teamname = teamname
        self._unum = unum
        self._pos = pos
        self._angle = angle
        self._vel = vel

    def type(self):
        return TrainerCommand.Type.MOVE

    def str(self):
        if not self.check():
            return ""

        if self._angle is None:
            return f"(move (player {self._teamname} {self._unum}) " \
                   f"{self._pos.x()} {self._pos.y()})"
        else:
            if self._vel is None:
                return f"(move (player {self._teamname} {self._unum})" \
                       f" {self._pos.x()} {self._pos.y()} {self._angle})"
            else:
                return f"(move (player {self._teamname} {self._unum}) " \
                       f"{self._pos.x()} {self._pos.y()} {self._angle}" \
                       f" {self._vel.x()} {self._vel.y()})"

    def check(self):
        if not 0 < self._unum < 12:
            print("Illegal uniform number")
            return False
        return True
