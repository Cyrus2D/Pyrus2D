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


# class PlayerChangeViewCommand(PlayerSupportCommand):
#     def __init__(self):


class PlayerSayCommand(PlayerSupportCommand):
    def __init__(self, msg: str, version: float):
        self_msg = msg
        self._version = version

    def str(self):
        return f"(say {self._msg}"