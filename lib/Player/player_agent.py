from lib.network.udp_socket import *
from lib.player_command.player_command import *

class WorldModel:
    pass


class PlayerAgent:
    def __init__(self):
        self._socket = UDPSocket(IPAddress('localhost', 6000))
        self._world = WorldModel()

    def run(self):
        self.connect()
        while True:
            message, server_address = self._socket.recieve_msg()
            self.pars_message(message)

    def connect(self):
        self._socket.send_msg(PlayerInitCommand("Pyrus", 15).str())

    def pars_message(self):