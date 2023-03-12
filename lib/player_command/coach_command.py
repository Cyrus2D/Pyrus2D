from enum import Enum, auto, unique

from lib.debug.debug import log


class CoachCommand:
    @unique
    class Type(Enum):
        INIT = auto()  # connection command
        BYE = auto()

        CHECK_BALL = auto()
        LOOK = auto()
        TEAM_NAMES = auto()

        EYE = auto()
        
        CHANGE_PLAYER_TYPE = auto()
        CHANGE_PLAYER_TYPES = auto()

        CLANG_FREEFORM = auto()
        FREEFORM = auto()
        
        TEAM_GRAPHIC = auto()
        COMPRESSION = auto()
        DONE = auto()

        ILLEGAL = auto()

    def __init__(self):
        pass

    def type(self):
        pass

    def str(self):
        pass


class CoachInitCommand(CoachCommand):
    def __init__(self, team_name: str, version: float, coach_name: str=""):
        self._team_name: str = team_name
        self._version: float = version
        self._coach_name: str = coach_name
    
    def type(self):
        return CoachCommand.Type.INIT
    
    def str(self):
        s = f"(init {self._team_name}"
        
        if len(self._coach_name) > 0:
            s += f" {self._coach_name}"
        s += f" (version {self._version}))"
        return s

class CoachLookCommand(CoachCommand):
    def __init__(self):
        return
    
    def type(self):
        return CoachCommand.Type.LOOK
    
    def str(self):
        return "(look)"

class CoachEyeCommand(CoachCommand):
    def __init__(self, on: bool):
        self._on: bool = on
    
    def type(self):
        return CoachCommand.Type.EYE
    
    def str(self):
        if self._on:
            return "(eye on)"
        return "(eye off)"

class CoachDoneCommand(CoachCommand):
    def __init__(self):
        pass
    
    def type(self):
        return CoachCommand.Type.DONE
    
    def str(self):
        return "(done)"

class CoachTeamnameCommand(CoachCommand):
    def __init__(self):
        pass
    
    def type(self):
        return CoachCommand.Type.TEAM_NAMES
    
    def str(self):
        return "(team_names)"
    
class CoachSendCommands(CoachCommand):
    @staticmethod
    def all_to_str(commands):
        commands_msg = ""
        for command in commands:
            commands_msg += command.str()  # TODO FIX THIS
        return commands_msg
    
class CoachChangePlayerTypeCommand(CoachCommand):
    def __init__(self, unum: int, type: int):
        self._unum = unum
        self._type = type
    
    def type(self):
        return CoachCommand.Type.CHANGE_PLAYER_TYPE
    
    def str(self):
        if not 0 <= self._type < 18: # TODO PLAYER PARAM
            log.os_log().error(f"(coach change player type) illegal type! type={type}")
            return ""
        
        return f"(change_player_type {self._unum} {self._type})"

class CoachFreeFormMessageCommand(CoachCommand):
    def __init__(self, message: str):
        self._message = message
    
    def type(self):
        return CoachCommand.Type.FREEFORM
    
    def str(self):
        return f'(say (freeform "{self._message}"))'