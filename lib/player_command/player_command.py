from enum import Enum, unique, auto


@unique
class CommandType(Enum):
    # connection commands
    INIT = auto()  # ! < server connection command
    RECONNECT = auto()  # ! < server reconnection command
    BYE = auto()  # ! < server disconnection command

    # base commands
    MOVE = auto()
    DASH = auto()
    TURN = auto()
    KICK = auto()
    CATCH = auto()
    TACKLE = auto()
    NECK = auto()

    # support commands
    TURN_NECK = auto()
    CHANGE_FOCUS = auto()
    CHANGE_VIEW = auto()
    SAY = auto()
    POINTTO = auto()
    ATTENTIONTO = auto()

    # mode change commands
    CLANG = auto()
    EAR = auto()

    # other commands
    SENSE_BODY = auto()
    SCORE = auto()
    COMPRESSION = auto()

    # synch_mode command
    DONE = auto()

    ILLEGAL = auto()


class PlayerCommand:
    def type(self):
        pass

    def str(self):
        return ""

    # def name(self):
    #     pass


class PlayerInitCommand(PlayerCommand):
    def __init__(self, team_name: str, version: float = None, golie: bool = False):
        self._team_name = team_name
        self._version = version
        self._goalie = golie

    def str(self):
        return f"(init {self._team_name}" + \
               (f" (version {self._version})" if self._version >= 4 else "") + \
               ("(goalie)" if self._goalie else "") + \
               ")"

    def type(self):
        return CommandType.INIT


class PlayerReconnectCommand(PlayerCommand):
    def __init__(self, team_name: str, unum: int):
        self._team_name = team_name
        self._unum = unum

    def str(self):
        return f"(reconnect {self._team_name} {self._unum})"

    def type(self):
        return CommandType.RECONNECT


class PlayerByeCommand:
    def __init__(self):
        pass

    def str(self):
        return "(bye)"

    def type(self):
        return CommandType.BYE
