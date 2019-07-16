from lib.player.player_agent import *


def main(team_name="Pyrus", goalie=False):
    player_agent = PlayerAgent()
    player_agent.run(team_name, goalie)


if __name__ == "__main__":
    main()
