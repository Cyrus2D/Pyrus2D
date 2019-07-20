import logging

from lib.debug.color import Color
from lib.debug.level import Level
from lib.math.vector_2d import Vector2D
from lib.rcsc.game_time import GameTime


class dlog:
    _name: str = ""
    _log_file: str = ""
    _formatter = logging.Formatter('%(message)s')
    _logger = None
    _commands: str = ""
    _time: GameTime = GameTime()

    def __init__(self):
        pass

    @staticmethod
    def setup_logger(name=None, log_file=None, level=logging.INFO):
        """Function setup as many loggers as you want"""

        if name is None:
            name = dlog._name
        if log_file is None:
            log_file = dlog._log_file

        handler = logging.FileHandler(log_file, 'w')
        handler.setFormatter(dlog._formatter)

        dlog._name = name
        dlog._log_file = log_file

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        dlog._logger = logger

    @staticmethod
    def name():
        return dlog._name

    @staticmethod
    def logger():
        return dlog.logger()

    @staticmethod
    def log_file():
        return dlog._log_file

    @staticmethod
    def debug(msg):
        return dlog._logger.debug(msg)

    @staticmethod
    def add_line(level: Level = Level.LEVEL_ANY,
                 start: Vector2D = None,
                 end: Vector2D = None,
                 color: Color = Color(hexa="red")):
        dlog._commands += f"{dlog._time.cycle()} {level.value} l {start.x} {start.y} {end.x} {end.y} {color}\n"

    @staticmethod
    def flush():
        if dlog._time is None or dlog._time.cycle() == 0: return
        dlog.debug(dlog._commands)
        dlog._commands = ""
