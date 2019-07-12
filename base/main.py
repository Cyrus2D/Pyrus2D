from lib.network.udp_socket import UDPSocket, IPAddress
from lib.parser import MessageRecieveParser
from lib.player_command.player_body_command import *
from lib.player_command.player_command import *


def main():
    udp = UDPSocket(IPAddress('127.0.0.1', 6000))
    udp.send_msg(PlayerInitCommand("Pyrus", 8).str())
    d, s = udp.recieve_msg()
    print(s[0], s[1])
    while True:
        udp2 = UDPSocket(IPAddress('127.0.0.1', s[1]))
        d, s = udp.recieve_msg()
        print(s, d)
        command = PlayerDashCommand(100, 90)
        udp2.send_msg(command.str())


if __name__ == "__main__":
    # main()
    # print("done")
    s = '(player_type (id 0)(player_speed_max 1.05)(stamina_inc_max 45)(player_decay 0.4)(inertia_moment 5)(dash_power_rate 0.006)(player_size 0.3)(kickable_margin 0.7)(kick_rand 0.1)(extra_stamina 50)(effort_max 1)(effort_min 0.6))'
    parser = MessageRecieveParser().parse(s)
    print(str(parser))
