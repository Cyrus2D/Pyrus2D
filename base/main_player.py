#!/usr/bin/python3
from lib.player.basic_client import BasicClient
from lib.player.player_agent import PlayerAgent
import sys


def main(team_name="Pyrus", goalie=False):
    agent = PlayerAgent()
    client = BasicClient()
    agent.init(client)

    client.run(agent)
    # agent.run(team_name, goalie)


if __name__ == "__main__":
    goalie = False
    if len(sys.argv) > 1 and sys.argv[1] == "g":
        goalie = True
    main(goalie=goalie)
