import socket

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
        # self._sock.settimeout(0.001)  # TODO isn't this risky?!?!?

    def send_msg(self, msg: str):
        if msg[-1] != '\0':
            msg += '\0'
        self._sock.sendto(msg.encode(), self._ip.tuple())

    def recieve_msg(self, message_and_address):
        message, server_address = self._sock.recvfrom(MAX_BUFF_SIZE)
        message_and_address.clear()
        message_and_address.append(message)
        message_and_address.append(server_address)

        return len(message)
