from base.decision import *
from lib.Player.world_model import WorldModel
from lib.network.udp_socket import UDPSocket, IPAddress
from lib.player_command.player_command import PlayerInitCommand
from lib.player_command.player_command_body import PlayerTurnCommand, PlayerDashCommand
from lib.rcsc.server_param import ServerParam


class PlayerAgent:
    def __init__(self):
        self._socket = UDPSocket(IPAddress('localhost', 6000))
        self._world = WorldModel()
        self._full_world = WorldModel()
        self._think_mode = True
        self._server_param = ServerParam()
        self.last_body_command = PlayerTurnCommand(0)

    def run(self):
        self.connect()
        while True:
            message, server_address = self._socket.recieve_msg()
            print(message, server_address)
            self.parse_message(message.decode())

            if self._think_mode:
                self.action()

    def connect(self):
        self._socket.send_msg(PlayerInitCommand("Pyrus", 15).str())

    def parse_message(self, message):
        if message.find("server_param") is not -1:
            print(message)
            self._server_param.parse(message)
        elif message.find("fullstate") is not -1 or message.find("player_type") is not -1 or message.find(
                "sense_body") is not -1 or message.find("init") is not -1 or message.find("(init") is not -1:
            self._full_world.parse(message)

    def do_dash(self, power, angle):
        self.last_body_command = PlayerDashCommand(power, angle)

    def do_turn(self, angle):
        self.last_body_command = PlayerTurnCommand(angle)

    def world(self):
        return self._world

    def full_world(self):
        return self._full_world

    def action(self):
        get_decision(self)
        command = self.last_body_command
        self._socket.send_msg(command.str())
