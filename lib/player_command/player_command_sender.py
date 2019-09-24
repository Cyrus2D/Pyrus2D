from lib.player_command.player_command import PlayerCommand
from lib.player_command.player_command_body import PlayerBodyCommand
from lib.player_command.player_command_support import PlayerSupportCommand


class PlayerSendCommands(PlayerCommand):
    @staticmethod
    def all_to_str(commands):
        commands_msg = ""
        last_body_command = PlayerCommand()
        for command in commands:
            if type(command) in PlayerBodyCommand.body_commands:
                last_body_command = command
            else:
                commands_msg += command.str()
        commands_msg = last_body_command.str() + commands_msg
        return commands_msg


class PlayerCommandReverser(PlayerCommand):
    @staticmethod
    def reverse(commands):
        for i in range(len(commands)):
            # if "_dir" in commands[i].__dict__:
            #     commands[i]._dir = PlayerCommandReverser.reverse_deg(commands[i]._dir)
            if "_moment" in commands[i].__dict__:
                commands[i]._moment = PlayerCommandReverser.reverse_deg(commands[i]._moment)

    @staticmethod
    def reverse_deg(direction):
        if direction > 0:
            direction = 180 - direction
        elif direction < 0:
            direction = 180 + direction
        return direction
