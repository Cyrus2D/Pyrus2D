from lib.network.udp_socket import UDPSocket, IPAddress
from lib.parser import MessageParser
from lib.player_command.player_body_command import *
from lib.player_command.player_command import *
from lib.Player.player_agent import *


def main():
    player_agent = PlayerAgent()
    player_agent.run()


if __name__ == "__main__":
    main()
