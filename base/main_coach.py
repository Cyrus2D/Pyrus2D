#!/usr/bin/python3
from lib.player.basic_client import BasicClient
from base.sample_coach import SampleCoach

import team_config
import sys


def main():
    agent = SampleCoach()
    if not agent.handle_start():
        agent.handle_exit()
        return
    agent.run()


if __name__ == "__main__":
    main()
