#!/usr/bin/python3
import argparse
import team_config

parser = argparse.ArgumentParser(description='Run a player or a coach')
parser.add_argument('--player', action='store_true', help='Run a player', default=True)
parser.add_argument('--coach', action='store_true', help='Run a coach')
parser.add_argument('--goalie', action='store_true', help='Run a goalie')
parser.add_argument('-t', '--team-name', help='Team name to display')
parser.add_argument('-H', '--host', help='Server IP address')
parser.add_argument('-p', '--player-port', help='Server Player port')
parser.add_argument('-P', '--coach-port', help='Server Coach port')
parser.add_argument('--trainer-port', help='Server Trainer port')
parser.add_argument('--log-path', help='Path to store logs')
parser.add_argument('--file-log-level', help='Log level for file')
parser.add_argument('--console-log-level', help='Log level for console')
parser.add_argument('--disable-file-log', action='store_true', help='Disable file logging')
args = parser.parse_args()

team_config.update_team_config(args)

from base.sample_coach import SampleCoach
from base.sample_player import SamplePlayer
import sys

        
def main():
    if args.player:
        agent = SamplePlayer()
    elif args.coach:
        agent = SampleCoach()
    elif args.goalie:
        agent = SamplePlayer(True)
    else:
        print("Please specify --player or --coach")
        return
        
    if not agent.handle_start():
        agent.handle_exit()
        return
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted. Exiting...")
        agent.handle_exit()
        sys.exit(0)
        
if __name__ == "__main__":
    main()