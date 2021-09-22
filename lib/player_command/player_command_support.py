from lib.player.sensor.see_state import SeeState
from lib.player_command.player_command import PlayerCommand, CommandType
from lib.rcsc.types import ViewWidth, ViewQuality


class PlayerSupportCommand(PlayerCommand):
    def type(self):
        pass

    def str(self):
        pass

    # def name(self):
    #     pass


class PlayerTurnNeckCommand(PlayerSupportCommand):
    def __init__(self, moment):
        self._moment = moment

    def str(self):
        return f"(turn_neck {self._moment})"

    def type(self):
        return CommandType.TURN_NECK

    def moment(self):
        return self._moment


class PlayerChangeViewCommand(PlayerSupportCommand):
    def __init__(self, w: ViewWidth, q: ViewQuality, version: float = 8.0):
        self._width: ViewWidth = w
        self._quality: ViewQuality = q
        self._version = version

    def type(self):
        return CommandType.CHANGE_VIEW

    def str(self):
        return f"(change_view {self._width}" + (f" {self._quality})" if not SeeState.synch_see_mode() else ")")

    def width(self):
        return self._width

    def quality(self):
        return self._quality


class PlayerSayCommand(PlayerSupportCommand):
    def __init__(self, msg: str, version: float):
        self._msg = msg
        self._version = version

    def str(self):
        tmp = self._msg
        if self._version >= 8:
            tmp = '"' + self._msg + '"'
        return f"(say {tmp})"

    def type(self):
        return CommandType.SAY

    def message(self):
        return self._msg

    def append(self, msg):
        self._msg += msg


class PlayerPointtoCommand(PlayerSupportCommand):
    def __init__(self, dist: float, dir: float, on: bool):
        self._dist = dist
        self._dir = dir  # relative to body angle
        self._on = on  # on/off switch

    def str(self):
        if self._on:
            return f"(pointto {self._dist} {self._dir})"
        else:
            return "(pointto off)"

    def type(self):
        return CommandType.POINTTO


# TODO Write other commands ...

class PlayerDoneCommand(PlayerSupportCommand):
    def __init__(self):
        pass

    def str(self):
        return "(done)"

    def type(self):
        return CommandType.DONE
