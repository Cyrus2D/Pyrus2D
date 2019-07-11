from lib.udp_socket import UDPSocket, IPAddress
from lib.player_command.player_body_command import *
from lib.player_command.player_command import *


def main():
    udp = UDPSocket(IPAddress('127.0.0.1', 6000))
    udp.send_msg(PlayerInitCommand("cr").str())
    while True:
        d, s = udp.recieve_msg()
        print(d)
        command = PlayerDashCommand(100, 90)
        udp.send_msg(command.str())


if __name__ == "__main__":
    main()
    print("done")
