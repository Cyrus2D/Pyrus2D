#!/usr/bin/python3
from base.sample_player import SamplePlayer
from lib.player.basic_client import BasicClient
from lib.player.player_agent import PlayerAgent
import sys
import team_config


def main(unum, goalie=False):
    agent = SamplePlayer()
    if not agent.handle_start():
        agent.handle_exit()
        return
    agent.run()


if __name__ == "__main__":
    goalie = False
    if len(sys.argv) == 1:
        raise Exception('Uniform number should be pass as argument!')
    unum = int(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2] == "g":
        goalie = True

    main(unum=unum, goalie=goalie)
