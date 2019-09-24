from lib.player_command.player_command import PlayerCommand, CommandType


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


# TODO kirie in :\
# class PlayerChangeViewCommand(PlayerSupportCommand):
#     def __init__(self):


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
