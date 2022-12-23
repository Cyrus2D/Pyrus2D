#!/usr/bin/python3
from lib.player.basic_client import BasicClient
from base.sample_coach import SampleCoach

import sys


def main(team_name="Pyrus"):
    agent = SampleCoach()
    client = BasicClient()
    agent.init(client)

    client.run(agent)
    # agent.run(team_name, goalie)


if __name__ == "__main__":
    main()
