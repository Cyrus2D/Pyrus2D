#!/usr/bin/python3

from lib.player.player_agent import *

def main(team_name="Pyrus", goalie=False):
    player_agent = PlayerAgent()
    player_agent.run(team_name, goalie)


if __name__ == "__main__":
    print(sys.argv)
    goalie = False
    if len(sys.argv) > 1 and sys.argv[1] == "g":
        goalie = True
    main(goalie=goalie)
