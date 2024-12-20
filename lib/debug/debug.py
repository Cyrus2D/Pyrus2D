import sys
from logging import Logger
import os
import team_config
from lib.debug.debug_client import DebugClient
from lib.debug.os_logger import get_logger
from lib.debug.sw_logger import SoccerWindow_Logger
from lib.rcsc.game_time import GameTime


class DebugLogger:
    def __init__(self):
        if not team_config.DISABLE_FILE_LOG and not os.path.exists(team_config.LOG_PATH):
            os.makedirs(team_config.LOG_PATH)
        self._sw_log: SoccerWindow_Logger = SoccerWindow_Logger('NA', 1, GameTime(0, 0))
        self._os_log: Logger = get_logger(0)
        self._debug_client: DebugClient = None

    def setup(self, team_name, unum, time):
        if not team_config.DISABLE_FILE_LOG and not os.path.exists(team_config.LOG_PATH):
            os.makedirs(team_config.LOG_PATH)
        self.set_stderr(unum)
        self._sw_log = SoccerWindow_Logger(team_name, unum, time)
        self._os_log = get_logger(unum)
        self._debug_client = DebugClient()

    def sw_log(self):
        return self._sw_log

    def os_log(self):
        return self._os_log

    def debug_client(self):
        return self._debug_client

    def update_time(self, t: GameTime):
        self._time.assign(t.cycle(), t.stopped_cycle())
        
    def set_stderr(self, unum):
        if team_config.DISABLE_FILE_LOG:
            return
        if unum == 'coach':
            file_name = 'coach.err'
        elif unum > 0:
            file_name = f'player-{unum}.err'
        else:
            file_name = f'coach-log.err'
        sys.stderr = open(os.path.join(team_config.LOG_PATH, file_name), 'w')


log = DebugLogger()
