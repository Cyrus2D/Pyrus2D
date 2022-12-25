#!/usr/bin/python3
from lib.player.basic_client import BasicClient
from base.sample_coach import SampleCoach

import team_config
import sys


def main():
    if team_config.OUT is team_config.OUT_OPTION.UNUM:
        sys.stdout = open(f"coach-log.txt", 'w')
        sys.stderr = open(f"coach-error.txt", 'w')
    
    agent = SampleCoach()
    client = BasicClient()
    agent.init(client)

    client.run(agent)
    # agent.run(team_name, goalie)


if __name__ == "__main__":
    main()
