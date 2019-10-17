from enum import Enum

from lib.network.udp_socket import IPAddress, UDPSocket
from lib.player.templates import SoccerAgent


class ClientMode(Enum):
    offline = 0
    Online = 1


class BasicClient:
    def __init__(self):
        self._client_mode = ClientMode.Online
        self._server_alive = True
        self._socket: UDPSocket = None
        # self._interval_ms = 10
        # self._compression_lvl = 0

    def connect_to(self,
                   host_port: IPAddress,
                   interval_ms=None):
        self._socket = UDPSocket(host_port)
        return True

    def run(self, agent):
        if self._client_mode == ClientMode.Online:
            self.run_online(agent)

        agent.handle_exit()

    def run_online(self, agent: SoccerAgent):
        if not agent.handle_start() or not self.is_server_alive():
            agent.handle_exit()
            return

        while self.is_server_alive():
            # TODO handle selects and rets and fds and timeout ... (I dont know what the hell are these)
            agent.handle_message()

    def set_server_alive(self, mode: bool):
        self._server_alive = mode

    def send_message(self, msg):
        # TODO check function's return
        return self._socket.send_msg(msg)

    def recv_message(self, msg_addr):
        return self._socket.recieve_msg(msg_addr)

    def message(self):
        pass

    def client_mode(self):
        return self._client_mode

    def is_server_alive(self):
        return self._server_alive
