from enum import Enum, unique, auto

from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.vector_2d import Vector2D

from lib.debug.debug import log
from lib.rcsc.types import GameModeType


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
        return "(team_names)"


class TrainerSendCommands(TrainerCommand):
    @staticmethod
    def all_to_str(commands):
        commands_msg = ""
        for command in commands:
            commands_msg += command.str()  # TODO FIX THIS
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


class TrainerRecoverCommand(TrainerCommand):
    def __init__(self):
        super().__init__()

    def type(self):
        return TrainerCommand.Type.RECOVER

    def str(self):
        return '(recover)'


class TrainerMovePlayerCommand(TrainerCommand):
    def __init__(self,
                 teamname: str,
                 unum: int,
                 pos: Vector2D,
                 angle: float = None,
                 vel: Vector2D = None):
        super().__init__()
        self._teamname = teamname.strip('"')
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
                       f"{self._pos.x():.2f} {self._pos.y():.2f} {self._angle:.2f}" \
                       f" {self._vel.x():.2f} {self._vel.y():.2f})"

    def check(self):
        if not 0 < self._unum < 12:
            log.os_log().error("Illegal uniform number")
            return False
        return True


class TrainerInitCommand(TrainerCommand):
    def __init__(self, version):
        super().__init__()
        self._version = version

    def type(self):
        return TrainerCommand.Type.INIT

    def str(self):
        return f"(init (version {self._version}))"


class TrainerDoneCommand(TrainerCommand):
    def __init__(self):
        super().__init__()

    def type(self):
        return TrainerCommand.Type.DONE

    def str(self):
        return "(done)"


class TrainerEyeCommand(TrainerCommand):
    def __init__(self, on: bool):
        super().__init__()
        self._on: bool = on

    def type(self):
        return TrainerCommand.Type.EYE

    def str(self):
        if self._on:
            return "(eye on)"
        return "(eye off)"


class TrainerEarCommand(TrainerCommand):
    def __init__(self, on: bool):
        super().__init__()
        self._on = on

    def type(self):
        return TrainerCommand.Type.EAR

    def str(self):
        if self._on:
            return "(ear on)"
        return "(ear off)"


class TrainerChangeModeCommand(TrainerCommand):
    def __init__(self, mode: GameModeType):
        super().__init__()
        self._mode: GameModeType = mode

    def type(self):
        return TrainerCommand.Type.CHANGE_MODE

    def str(self):
        return f"(change_mode {self._mode.value})"
