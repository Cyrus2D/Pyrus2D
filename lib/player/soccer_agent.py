import argparse

import team_config
from lib.player.basic_client import BasicClient


class SoccerAgent:
    def __init__(self):
        self.parse_arguments()
        self._client: BasicClient = BasicClient()

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Start the Team. Runs the players and the coach.')

        parser.add_argument('-t', '--team-name',
                            help='Team name to display')

        parser.add_argument('-o', '--out',
                            help='Output type(values->[std, textfile]). std for print on standard stream, unum for print to seperated files.')

        parser.add_argument('-H', '--host',
                            help='Server IP address')

        parser.add_argument('-p', '--player-port',
                            help='Server Player port')

        parser.add_argument('-P', '--coach-port',
                            help='Server Coach port')

        parser.add_argument('--trainer-port',
                            help='Server Trainer port')

        parser.add_argument('-g', '--goalie',
                            help='Server Trainer port',
                            action='store_true')
        parser.add_argument("-n",help="number of players",type=int,default=11)
        args = parser.parse_args()

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

        if args.goalie:
            self._goalie = True


    def init_impl(self, goalie: bool) -> bool:
        pass

    def handle_start(self) -> bool:
        pass

    def run(self):
        pass

    def handle_exit(self):
        pass

