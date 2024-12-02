#!/usr/bin/python3
import argparse
from lib.player.basic_client import BasicClient
from base.sample_coach import SampleCoach
from base.sample_player import SamplePlayer
import team_config
import logging


def update_team_config(args):
    if args.team_name:
        team_config.TEAM_NAME = args.team_name

    if args.out:
        team_config.OUT = team_config.OUT_OPTION(args.out)

    if args.host:
        team_config.HOST = args.host

    if args.player_port:
        team_config.PLAYER_PORT = args.player_port

    if args.coach_port:
        team_config.COACH_PORT = args.coach_port

    if args.trainer_port:
        team_config.TRAINER_PORT = args.trainer_port
        
    if args.log_path:
        team_config.LOG_PATH = args.log_path
    
    if args.file_log_level:
        team_config.FILE_LOG_LEVEL = getattr(logging, args.file_log_level.upper(), logging.INFO)

    if args.console_log_level:
        team_config.CONSOLE_LOG_LEVEL = getattr(logging, args.console_log_level.upper(), logging.INFO)
        
def main():
    parser = argparse.ArgumentParser(description='Run a player or a coach')
    parser.add_argument('--player', action='store_true', help='Run a player')
    parser.add_argument('--coach', action='store_true', help='Run a coach')
    parser.add_argument('--goalie', action='store_true', help='Run a goalie')
    parser.add_argument('-t', '--team-name', help='Team name to display')
    parser.add_argument('-o', '--out', help='Output type(values->[std, textfile]). std for print on standard stream, unum for print to seperated files.')
    parser.add_argument('-H', '--host', help='Server IP address')
    parser.add_argument('-p', '--player-port', help='Server Player port')
    parser.add_argument('-P', '--coach-port', help='Server Coach port')
    parser.add_argument('--trainer-port', help='Server Trainer port')
    parser.add_argument('--log-path', help='Path to store logs')
    parser.add_argument('--file-log-level', help='Log level for file')
    parser.add_argument('--console-log-level', help='Log level for console')
    args = parser.parse_args()
    
    update_team_config(args)
    
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
    agent.run()
        
if __name__ == "__main__":
    main()