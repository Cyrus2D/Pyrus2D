import socket

import team_config

MAX_BUFF_SIZE = 8192


class IPAddress:
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port

    def tuple(self) -> tuple:
        return self.ip(), self.port()

    def __repr__(self):
        return self.ip(), self.port()

    def __str__(self):
        return f"({self.ip()}:{self.port()}"

    def ip(self):
        return self._ip

    def port(self):
        return self._port


class UDPSocket:
    def __init__(self, ip_address: IPAddress):
        self._ip: IPAddress = ip_address
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(team_config.SOCKET_INTERVAL)
        self._receive_first_message = False

    def send_msg(self, msg: str):
        if msg[-1] != '\0':
            msg += '\0'
        return self._sock.sendto(msg.encode(), self._ip.tuple())

    def receive_msg(self):
        try:
            message, server_address = self._sock.recvfrom(MAX_BUFF_SIZE)
            if not self._receive_first_message:
                self._receive_first_message = True
                self._ip._port = server_address[1]
            return len(message), message, server_address
        except:
            message = ""
            server_address = 0
            return len(message), message, server_address
