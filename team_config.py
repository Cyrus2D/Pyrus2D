from enum import Enum
import datetime
import logging


class OUT_OPTION(Enum):
    STDOUT = 'std'
    TEXTFILE = 'textfile'


TEAM_NAME = "PYRUS"
LOG_PATH = f'logs/{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}'
FILE_LOG_LEVEL = logging.ERROR
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
