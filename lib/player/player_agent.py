import time
from lib.math.geom_2d import *
from base.decision import get_decision
from lib.debug.logger import *
from lib.player.soccer_agent import SoccerAgent
from lib.player.world_model import WorldModel
from lib.network.udp_socket import UDPSocket, IPAddress
from lib.player_command.player_command import PlayerInitCommand, PlayerByeCommand
from lib.player_command.player_command_body import PlayerTurnCommand, PlayerDashCommand, PlayerMoveCommand, \
    PlayerKickCommand
from lib.player_command.player_command_support import PlayerDoneCommand
from lib.player_command.player_command_sender import PlayerSendCommands
from lib.rcsc.server_param import ServerParam


class PlayerAgent(SoccerAgent):
    class Impl:
        def __init__(self, agent):
            # TODO so many things....
            self._agent: PlayerAgent = agent
            pass

        def send_init_command(self):
            # TODO check reconnections

            # TODO make config class for these datas
            com = PlayerInitCommand("Pyrus", 15, False)

            if self._agent._client.send_message(com.str()) <= 0:
                print("ERROR faild to connect to server")
                self._agent._client.set_server_alive(False)

        def send_bye_command(self):
            com = PlayerByeCommand()
            self._agent._client.send_message(com.str())
            self._agent._client.set_server_alive(False)

    def __init__(self):
        super().__init__()
        self._impl: PlayerAgent.Impl = PlayerAgent.Impl()

    def handle_start(self):
        if self._client is None:
            return False

        # TODO check for config.host not empty

        if not self._client.connect_to(IPAddress('localhost', 6000)):
            print("ERROR faild to connect to server")
            self._client.set_server_alive(False)
            return False

        self._impl.send_init_command()
        return True

    def handle_exit(self):
        if self._client.is_server_alive():
            self._impl.send_bye_command()
        print(f"player({self._unum}: finished")


class PlayerAgent:
    def __init__(self):
        self._socket = UDPSocket(IPAddress('localhost', 6000))
        self._world = WorldModel()
        self._full_world = WorldModel()
        self._think_mode = False
        self._is_synch_mode = True
        self._last_body_command = []
        self.is_run = True

    def run(self, team_name, goalie):
        self.connect(team_name, goalie)
        self._full_world._team_name = team_name
        last_time_rec = time.time()

        sum_think_time = 0
        n_think = 0
        while True:
            message_and_address = []
            message_count = 0
            cycle_start = time.time()
            while True:
                self._socket.recieve_msg(message_and_address)
                message = message_and_address[0]
                server_address = message_and_address[1]
                if len(message) != 0:
                    self.parse_message(message.decode())
                elif time.time() - last_time_rec > 3:
                    self.is_run = False
                    break
                message_count += 1
                if self._think_mode:
                    last_time_rec = time.time()
                    break
            cycle_end = time.time()
            # print(f"run-time: {cycle_end-cycle_start}s")

            if not self.is_run:
                print("srever down")
                break

            if message_count > 0:
                self.action()
            elif self._think_mode:
                self.action()

                # if self.world().game_mode().mode_name() == "play_on":
                #     n_think += 1
                #     sum_think_time += cycle_end - cycle_start
                #     print(f"avg_think_time={sum_think_time/n_think}s")
            self._think_mode = False

    def connect(self, team_name, goalie, version=15):
        self._socket.send_msg(PlayerInitCommand(team_name, version, goalie).str())

    def parse_message(self, message):
        # print("#" * 20)
        # print(message)
        # self._think_mode = False
        if message.find("(init") is not -1:
            self.init_dlog(message)
        if message.find("server_param") is not -1:
            ServerParam.i().parse(message)
        elif message.find("fullstate") is not -1 or message.find("player_type") is not -1 or message.find(
                "sense_body") is not -1 or message.find("(init") is not -1:
            self._full_world.parse(message)
            dlog._time = self.world().time()
        elif message.find("think") is not -1:
            self._think_mode = True

    def do_dash(self, power, angle=0):
        self._last_body_command.append(PlayerDashCommand(power, float(angle)))
        return True

    def do_turn(self, angle):
        self._last_body_command.append(PlayerTurnCommand(float(angle)))
        return True

    def do_move(self, x, y):
        self._last_body_command.append(PlayerMoveCommand(x, y))
        return True

    def do_kick(self, power: float, rel_dir: AngleDeg):
        self._last_body_command.append(PlayerKickCommand(power, rel_dir))
        return True

    def world(self) -> WorldModel:
        return self._full_world

    def full_world(self) -> WorldModel:
        return self._full_world

    def action(self):
        if (self.world().self_unum() is None
                or self.world().self().unum() != self.world().self_unum()):
            return
        get_decision(self)
        commands = self._last_body_command
        # if self.world().our_side() == SideID.RIGHT:
        # PlayerCommandReverser.reverse(commands) # unused :\ # its useful :) # nope not useful at all :(
        if self._is_synch_mode:
            commands.append(PlayerDoneCommand())
        self._socket.send_msg(PlayerSendCommands.all_to_str(commands))
        dlog.flush()
        self._last_body_command = []

    def init_dlog(self, message):
        message = message.split(" ")
        unum = int(message[2])
        side = message[1]
        dlog.setup_logger(f"dlog{side}{unum}", f"/tmp/{self.world().team_name()}-{unum}.log", logging.DEBUG)
