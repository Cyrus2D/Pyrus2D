from enum import Enum
import datetime
import logging


TEAM_NAME = "PYRUS"
LOG_PATH = f'logs/{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}'
FILE_LOG_LEVEL = logging.ERROR
DISABLE_FILE_LOG = False
CONSOLE_LOG_LEVEL = logging.ERROR
HOST = 'localhost'
PLAYER_PORT = 6000
TRAINER_PORT = 6001
COACH_PORT = 6002
DEBUG_CLIENT_PORT = 6032

SOCKET_INTERVAL = 0.01
WAIT_TIME_THR_SYNCH_VIEW = 30
WAIT_TIME_THR_NOSYNCH_VIEW = 75

PLAYER_VERSION = 18
COACH_VERSION = 18

WORLD_IS_REAL_WORLD = True
S_WORLD_IS_REAL_WORLD = False

USE_COMMUNICATION = True


def update_team_config(args):
    import team_config
    if args.team_name:
        team_config.TEAM_NAME = args.team_name

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
        
    if args.disable_file_log:
        team_config.DISABLE_FILE_LOG = args.disable_file_log