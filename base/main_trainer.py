#!/usr/bin/python3
from base.sample_trainer import SampleTrainer
from lib.player.basic_client import BasicClient

import sys


def main():
    agent = SampleTrainer()
    if not agent.handle_start():
        agent.handle_exit()
        return
    agent.run()


if __name__ == "__main__":
    goalie = False
    # if len(sys.argv) > 1 and sys.argv[1] == "g":
    main()
