from enum import Enum


class OUT_OPTION(Enum):
    STDOUT = 'std'
    UNUM= 'unum'

TEAM_NAME = "PYRUS"
OUT = OUT_OPTION.STDOUT
HOST= 'localhost'
PLAYER_PORT = 6000
TRAINER_PORT = 6001
COACH_PORT = 6002
DEBUG_CLIENT_PORT = 6032

SOCKET_INTERVAL = 0.01
WAIT_TIME_THR_SYNCH_VIEW = 30
WAIT_TIME_THR_NOSYNCH_VIEW = 75

PLAYER_VERSION = 18
COACH_VERSION = 18

FULL_STATE_DEBUG = True
USE_COMMUNICATION = True
