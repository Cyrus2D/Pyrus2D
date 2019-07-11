from src.player_command.player_command import PlayerCommand, CommandType


class PlayerBodyCommand(PlayerCommand):
    def type(self):
        pass

    def str(self):
        pass

    # def name(self):
    #     pass


class PlayerMoveCommand(PlayerBodyCommand):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def str(self):
        return f"(move {self._x} {self._y})"

    def type(self):
        return CommandType.MOVE


class PlayerDashCommand(PlayerBodyCommand):
    def __init__(self, power, dir):
        self._power = power
        self._dir = dir

    def str(self):
        return f"(dash {self._power}" + (f" {self._dir})" if self._dir != 0 else ")")

    def type(self):
        return CommandType.DASH


class PlayerTurnCommand(PlayerBodyCommand):
    def __init__(self, moment: float):
        self._moment = moment

    def str(self):
        return f"(turn {self._moment})"

    def type(self):
        return CommandType.TURN


class PlayerKickCommand(PlayerBodyCommand):
    def __init__(self, power, dir):
        self._power = power
        self._dir = dir  # relative to body angle

    def str(self):
        return f"(kick {self._power} {self._dir})"

    def type(self):
        return CommandType.KICK

    def kick_power(self):
        return self._power

    def kick_dir(self):
        return self._dir


class PlayerCatchCommand(PlayerBodyCommand):
    def __init__(self, dir):
        self._dir = dir

    def str(self):
        return f"(catch {self._dir})"

    def type(self):
        return CommandType.CATCH


class PlayerTackleCommand(PlayerBodyCommand):
    def __init__(self, power_or_dir, foul: bool = False):
        self._power_or_dir = power_or_dir
        self._foul = foul

    def str(self):
        return f"(tackle {self._power_or_dir}" + (f" on)" if self._foul else ")")

    def type(self):
        return CommandType.TACKLE
