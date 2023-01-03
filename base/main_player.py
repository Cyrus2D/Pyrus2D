#!/usr/bin/python3
from base.sample_player import SamplePlayer
from lib.player.basic_client import BasicClient
from lib.player.player_agent import PlayerAgent
import sys
import team_config


def main(unum, goalie=False):
    if team_config.OUT is team_config.OUT_OPTION.UNUM:
        sys.stdout = open(f"player-{unum}-log.txt", 'w')
        sys.stderr = open(f"player-{unum}-error.txt", 'w')
    
    agent = SamplePlayer()
    client = BasicClient()
    agent.init(client, goalie)

    client.run(agent)
    # agent.run(team_name, goalie)


if __name__ == "__main__":
    goalie = False
    if len(sys.argv) > 1 and sys.argv[1] == "g":
        goalie = True
    main(goalie=goalie)
