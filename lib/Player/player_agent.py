from lib.network.udp_socket import *
from lib.player_command.player_command import *
from lib.player_command.player_body_command import *
from lib.server_param import *
from lib.Player.world_model import *


class PlayerAgent:
    def __init__(self):
        self._socket = UDPSocket(IPAddress('localhost', 6000))
        self._world = WorldModel()
        self._full_world = WorldModel()
        self._think_mode = True
        self._server_param = ServerParam()

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
        elif message.find("fullstate") is not -1 or message.find("player_type") is not -1 or message.find("sense_body") is not -1 or message.find("init") is not -1:
            self._full_world.parse(message)

    def action(self):
        command = PlayerDashCommand(100, 10)
        self._socket.send_msg(command.str())
