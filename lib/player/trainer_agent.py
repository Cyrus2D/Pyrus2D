import logging
import time

from lib.action.kick_table import KickTable
from lib.debug.logger import dlog
from lib.math.angle_deg import AngleDeg
from lib.math.vector_2d import Vector2D
from lib.network.udp_socket import IPAddress
from lib.coach.gloabl_world_model import GlobalWorldModel
from lib.player.soccer_agent import SoccerAgent
from lib.player_command.player_command_sender import PlayerSendCommands
from lib.player_command.player_command_support import PlayerDoneCommand
from lib.player_command.trainer_command import TrainerTeamNameCommand, TrainerSendCommands, TrainerMoveBallCommand, \
    TrainerMovePlayerCommand, TrainerInitCommand
from lib.rcsc.server_param import ServerParam


class TrainerAgent(SoccerAgent):
    class Impl:
        def __init__(self, agent):
            # TODO so many things....
            self._agent: TrainerAgent = agent
            self._think_received = False

        def send_init_command(self):
            # TODO check reconnection

            # TODO make config class for these data
            com = TrainerInitCommand(15)
            # TODO set team name from config
            self._agent._full_world._team_name = "Pyrus"

            if self._agent._client.send_message(com.str()) <= 0:
                print("ERROR failed to connect to server")
                self._agent._client.set_server_alive(False)

        def send_bye_command(self):
            self._agent._client.set_server_alive(False)

        @property
        def think_received(self):
            return self._think_received

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

        if not self._client.connect_to(IPAddress('localhost', 6001)):
            print("ERROR failed to connect to server")
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
                print("MESSSAGE:", message)
                server_address = message_and_address[1]
                if len(message) != 0:
                    self.parse_message(message.decode())
                elif time.time() - last_time_rec > 3:
                    self._client.set_server_alive(False)
                    break
                message_count += 1
                if self._impl.think_received:
                    last_time_rec = time.time()
                    break

            if not self._client.is_server_alive():
                print("Pyrus Agent : Server Down")
                # print("Pyrus Agent", self._world.self_unum(), ": Server Down")
                break

            if self._impl.think_received:
                self.action()
                self._impl._think_received = False
            # TODO elif for not sync mode

    def parse_message(self, message):
        if message.find("(init") is not -1:
            self.init_dlog(message)
        if message.find("server_param") is not -1:
            ServerParam.i().parse(message)

            # TODO make function for these things
            if KickTable.instance().createTables():
                print("KICKTABLE CREATE")
            else:
                print("KICKTABLE Faild")
        elif message.find("fullstate") is not -1 or message.find("player_type") is not -1 or message.find(
                "sense_body") is not -1 or message.find("(init") is not -1:
            self._full_world.parse(message)
            dlog._time = self.world().time()
        elif message.find("think") is not -1:
            self._impl._think_received = True

    def init_dlog(self, message):
        dlog.setup_logger(f"dlog-coach", f"/tmp/{self.world().team_name()}-coach.log", logging.DEBUG)

    def world(self) -> GlobalWorldModel:
        return self._full_world

    def full_world(self) -> GlobalWorldModel:
        return self._full_world

    def action(self):
        if (self.world().self_unum() is None
                or self.world().self().unum() != self.world().self_unum()):
            return
        self.action_impl()
        commands = self._last_body_command
        # if self.world().our_side() == SideID.RIGHT:
        # PlayerCommandReverser.reverse(commands) # unused :\ # its useful :) # nope not useful at all :(
        if self._is_synch_mode:
            commands.append(PlayerDoneCommand())
        self._client.send_message(PlayerSendCommands.all_to_str(commands))
        dlog.flush()
        self._last_body_command = []

    def action_impl(self):
        pass

    def do_teamname(self):
        command = TrainerTeamNameCommand()
        return self.send_command(command)

    def send_command(self, commands):  # TODO it should be boolean
        self._client.send_message(TrainerSendCommands.all_to_str(commands))

    def do_move_ball(self, pos: Vector2D, vel: Vector2D = Vector2D(0, 0)):
        command = TrainerMoveBallCommand(pos, vel)
        return self.send_command(command)

    def do_move_player(self,
                       teamname: str,
                       unum: int,
                       pos: Vector2D,
                       angle: AngleDeg = None,
                       vel: Vector2D = None):
        command = TrainerMovePlayerCommand(teamname, unum, pos, angle, vel)
        return self.send_command(command)
