import argparse
from time import sleep
import base.main_player as main_p
import base.main_coach as main_c
import multiprocessing as mp
import team_config


parser = argparse.ArgumentParser(description='Start the Team. Runs the players and the coach.')


parser.add_argument('-t', '--team-name',
                    help='Team name to display')

parser.add_argument('-o', '--out',
                    help='Output type(values->[std, unum]). std for print on standard stream, unum for print to seperated files.')

parser.add_argument('-H', '--host',
                    help='Server IP address')

parser.add_argument('-p', '--player-port',
                    help='Server Player port')

parser.add_argument('-P', '--coach-port',
                    help='Server Coach port')

parser.add_argument('--trainer-port',
                    help='Server Trainer port')
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

players = []

goalie = mp.Process(target=main_p.main, args=(1,True))
goalie.start()

players.append(goalie)

for i in range(2,11):
    proc = mp.Process(target=main_p.main, args=(i,False))
    proc.start()
    players.append(proc)
    sleep(0.25)

sleep(5)

coach = mp.Process(target=main_c.main)
coach.start()