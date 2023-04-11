from enum import Enum

from lib.network.udp_socket import IPAddress, UDPSocket

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.soccer_agent import SoccerAgent


class BasicClient:
    def __init__(self):
        self._server_alive = True
        self._socket: UDPSocket = None

    def connect_to(self,
                   host_port: IPAddress):
        self._socket = UDPSocket(host_port)
        return True

    def set_server_alive(self, mode: bool):
        self._server_alive = mode

    def send_message(self, msg):
        # TODO check function's return
        return self._socket.send_msg(msg)

    def recv_message(self):
        return self._socket.receive_msg()

    def message(self):
        pass

    def is_server_alive(self):
        return self._server_alive
