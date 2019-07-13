from lib.network.udp_socket import *
from lib.parser import MessageParser
from lib.player_command.player_command import *
from lib.player_command.player_body_command import *
from lib.server_param import *


class WorldModel:
    pass


class PlayerAgent:
    def __init__(self):
        self._socket = UDPSocket(IPAddress('localhost', 6000))
        self._world = WorldModel()
        self._full_world = WorldModel()
        self._think_mode = False
        self._server_param = ServerParam

    def run(self):
        self.connect()
        while True:
            message, server_address = self._socket.recieve_msg()
            self.parse_message(message)

            if self._think_mode:
                self.action()

    def connect(self):
        self._socket.send_msg(PlayerInitCommand("Pyrus", 15).str())

    def parse_message(self, message):
        message = ""
        if message.find("server_param"):
            self._server_param.parse(message)

        dic = MessageParser().parse(string)
        if dic['server_param']:
            SP.i.set_data(dic)
        elif dic['player_type']:
            player_type.append(dic) # TODO where and how define PLAYER TYPE

    def action(self):
        command = PlayerDashCommand(100, 90)
        self._socket.send_msg(command.str())
