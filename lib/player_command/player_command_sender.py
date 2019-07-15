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
        print("message", commands_msg)
        return commands_msg
