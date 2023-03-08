import logging
import time

from lib.debug.logger import dlog
from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.vector_2d import Vector2D
from lib.network.udp_socket import IPAddress
from lib.coach.gloabl_world_model import GlobalWorldModel
from lib.player.soccer_agent import SoccerAgent
from lib.player_command.trainer_command import TrainerTeamNameCommand, TrainerSendCommands, TrainerMoveBallCommand, \
    TrainerMovePlayerCommand, TrainerInitCommand, TrainerDoneCommand, TrainerEyeCommand, TrainerEarCommand, \
    TrainerChangeModeCommand, TrainerRecoverCommand
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType
from lib.debug.debug_print import debug_print

import team_config


class TrainerAgent(SoccerAgent):
    class Impl:
        def __init__(self, agent):
            # TODO so many things....
            self._agent: TrainerAgent = agent
            self._think_received = True
            self._game_mode: GameMode = GameMode()
            self._current_time: GameTime = GameTime()

        def hear_parser(self, message: str):
            _, sender, cycle = tuple(
                message.split(" ")[:3]
            )
            if cycle.isnumeric():
                cycle = int(cycle)
            else:
                return

            if sender[0].isnumeric() or sender[0] == '-':  # PLAYER MESSAGE
                self.hear_player_parser(message)
            elif sender == "referee":
                self.hear_referee_parser(message)

        def hear_player_parser(self, message):
            pass

        def hear_referee_parser(self, message: str):
            mode = message.split(" ")[-1].strip(")")
            self._game_mode.update(mode, self._current_time)

            # TODO CARDS AND OTHER STUFF

            if self._game_mode.type() is GameModeType.TimeOver:
                self.send_bye_command()
                return
            self._agent.world().update_game_mode(self._game_mode, self._current_time)
            # TODO FULL STATE WORLD update
        def send_init_command(self):
            # TODO check reconnection

            # TODO make config class for these data
            com = TrainerInitCommand(team_config.COACH_VERSION)

            if self._agent._client.send_message(com.str()) <= 0:
                debug_print("ERROR failed to connect to server")
                self._agent._client.set_server_alive(False)

        def send_bye_command(self):
            self._agent._client.set_server_alive(False)

        @property
        def think_received(self):
            return self._think_received

        def analyze_init(self, message):
            self._agent.init_dlog(message)
            self._agent.do_eye(True)
            self._agent.do_ear(True)

    def __init__(self):
        super().__init__()
        self._impl: TrainerAgent.Impl = TrainerAgent.Impl(self)
        self._world = GlobalWorldModel()
        self._full_world = GlobalWorldModel()
        self._is_synch_mode = True
        self._last_body_command = []

    def handle_message(self):
        self.run()

    def handle_start(self):
        if self._client is None:
            return False

        # TODO check for config.host not empty

        if not self._client.connect_to(IPAddress(team_config.HOST, team_config.TRAINER_PORT)):
            debug_print("ERROR failed to connect to server")
            self._client.set_server_alive(False)
            return False

        self._impl.send_init_command()
        return True

    def run(self):
        last_time_rec = time.time()
        while True:
            message_and_address = []
            message_count = 0
            while True:
                self._client.recv_message(message_and_address)
                message = message_and_address[0]
                server_address = message_and_address[1]
                if len(message) != 0:
                    self.parse_message(message.decode())
                    last_time_rec = time.time()
                    break
                elif time.time() - last_time_rec > 3:
                    ("TIME")
                    self._client.set_server_alive(False)
                    break
                message_count += 1
                if self._impl.think_received:
                    last_time_rec = time.time()
                    break

            if not self._client.is_server_alive():
                debug_print(f"{team_config.TEAM_NAME} Agent : Server Down")
                break

            if self._impl.think_received:
                self.action()
                self._impl._think_received = False
            # TODO elif for not sync mode

    def parse_message(self, message):
        if message.find("(init") is not -1:
            self._impl.analyze_init(message)
        if message.find("server_param") is not -1:
            ServerParam.i().parse(message)
        elif message.find("(see") is not -1 or message.find("(player_type") is not -1:
            self._full_world.parse(message)
            self._impl._think_received = False
            dlog._time = self.world().time().copy()
        elif message.find("think") is not -1:
            self._impl._think_received = True
        elif message.find("(ok") is not -1:
            self._client.send_message(TrainerDoneCommand().str())
        elif message.find("(hear") is not -1:
            self._impl.hear_parser(message)

    def init_dlog(self, message):
        dlog.setup_logger(f"dlog-coach", f"/tmp/{self.world().team_name_l()}-coach.log", logging.DEBUG)

    def world(self) -> GlobalWorldModel:
        return self._full_world

    def full_world(self) -> GlobalWorldModel:
        return self._full_world

    def action(self):
        self.action_impl()
        commands = self._last_body_command
        # if self.world().our_side() == SideID.RIGHT:
        # PlayerCommandReverser.reverse(commands) # unused :\ # its useful :) # nope not useful at all :(
        commands.append(TrainerDoneCommand())
        # self._client.send_message(TrainerSendCommands.all_to_str(commands))
        for com in commands:
            self._client.send_message(com.str())
        dlog.flush()
        self._last_body_command = []

    def action_impl(self):
        pass

    def do_teamname(self):
        command = TrainerTeamNameCommand()
        self._last_body_command.append(command)
        return True

    def send_command(self, commands):  # TODO it should be boolean
        self._client.send_message(TrainerSendCommands.all_to_str(commands))

    def do_move_ball(self, pos: Vector2D, vel: Vector2D = Vector2D(0, 0)):
        command = TrainerMoveBallCommand(pos, vel)
        self._last_body_command.append(command)
        return True

    def do_move_player(self,
                       teamname: str,
                       unum: int,
                       pos: Vector2D,
                       angle: AngleDeg = None,
                       vel: Vector2D = None):
        command = TrainerMovePlayerCommand(teamname, unum, pos, angle, vel)
        self._last_body_command.append(command)
        return True

    def do_recover(self):
        command = TrainerRecoverCommand()
        self._last_body_command.append(command)
        return True

    def do_eye(self, on: bool):
        self._client.send_message(TrainerEyeCommand(on).str())

    def do_ear(self, on: bool):
        self._client.send_message(TrainerEarCommand(on).str())

    def do_change_mode(self, mode: GameModeType):
        self._last_body_command.append(TrainerChangeModeCommand(mode))
