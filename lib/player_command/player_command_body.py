from lib.player_command.player_command import PlayerCommand, CommandType


class PlayerBodyCommand(PlayerCommand):
    body_commands = []

    def type(self) -> CommandType:
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

    def __repr__(self):
        return "(Move To {}, {})".format(self._x, self._y)

    def type(self):
        return CommandType.MOVE


class PlayerDashCommand(PlayerBodyCommand):
    def __init__(self, power, direction):
        self._power = power
        self._dir = direction

    def str(self):
        return f"(dash {self._power:.2f}" + (f" {self._dir:.2f})" if self._dir != 0 else ")")

    def __repr__(self):
        return "(Dash power:{}, dir:{})".format(self._power, self._dir)

    def type(self):
        return CommandType.DASH


class PlayerTurnCommand(PlayerBodyCommand):
    def __init__(self, moment: float):
        self._moment = moment

    def str(self):
        return f"(turn {self._moment:.2f})"

    def __repr__(self):
        return "(Turn moment:{})".format(self._moment)

    def type(self):
        return CommandType.TURN


class PlayerKickCommand(PlayerBodyCommand):
    def __init__(self, power, rel_dir):
        self._power = power
        self._dir = rel_dir  # relative to body angle

    def str(self):
        return f"(kick {self._power:.2f} {self._dir:.2f})"

    def __repr__(self):
        return "(Kick power:{}, dir:{})".format(self._power, self._dir)

    def type(self):
        return CommandType.KICK

    def kick_power(self):
        return self._power

    def kick_dir(self):
        return self._dir


class PlayerCatchCommand(PlayerBodyCommand):
    def __init__(self, direction):
        self._dir = direction

    def str(self):
        return f"(catch {self._dir})"

    def __repr__(self):
        return "(Catch dir:{})".format(self._dir)

    def type(self):
        return CommandType.CATCH


class PlayerTackleCommand(PlayerBodyCommand):  # TODO Foul ...
    def __init__(self, power_or_dir, foul: bool = False):
        self._power_or_dir = power_or_dir
        self._foul = foul

    def str(self):
        return f"(tackle {self._power_or_dir}" + (f" on)" if self._foul else ")")

    def __repr__(self):
        return "(Tackle power{}, foul{})".format(self._power_or_dir, self._foul)

    def type(self):
        return CommandType.TACKLE


PlayerBodyCommand.body_commands = [PlayerMoveCommand,
                                   PlayerDashCommand,
                                   PlayerTurnCommand,
                                   PlayerKickCommand,
                                   PlayerCatchCommand,
                                   PlayerTackleCommand]
