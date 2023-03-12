import team_config
from lib.debug.os_logger import get_logger
from lib.debug.sw_logger import SoccerWindow_Logger
from lib.player.debug_client import DebugClient


class Debug:
    def __init__(self):
        self._sw_log: SoccerWindow_Logger = None
        self._os_log = None
        self._debug_client = None

    def setup(self, team_name, unum):
        self._sw_log: SoccerWindow_Logger = SoccerWindow_Logger(team_name, unum)
        self._os_log = get_logger(unum, team_config.OUT == team_config.OUT_OPTION.UNUM)
        self._debug_client = DebugClient()
