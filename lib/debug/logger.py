import logging

from lib.debug.color import Color
from lib.debug.level import Level
from lib.math.circle_2d import Circle2D
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
                 x1: float = None,
                 y1: float = None,
                 x2: float = None,
                 y2: float = None,
                 start: Vector2D = None,
                 end: Vector2D = None,
                 color: Color = Color(string="red")):
        if x1 is not None:
            dlog._commands += f"{dlog._time} {level.value} l {x1} {y1} {x2} {y2} {color}\n"
        elif start is not None:
            dlog.add_line(level, start.x(), start.y(), end.x(), end.y(), color=color)

    @staticmethod
    def add_text(level: Level = Level.LEVEL_ANY, message: str = ""):
        dlog._commands += f"{dlog._time} {level.value} M {message}\n"  # TODO flush if message size is so large like 8192 and bigger

    @staticmethod
    def add_circle(level: Level = Level.LEVEL_ANY,
                   r: float = None,
                   cx: float = None,
                   cy: float = None,
                   center: Vector2D = None,
                   cicle: Circle2D = None,
                   fill: bool = False,
                   color: Color = Color(string='red'), ):
        if cx is not None:
            dlog._commands += f"{dlog._time} {level.value} {'C' if fill else 'c'} {cx} {cy} {r} {color}\n"
        elif center is not None:
            dlog.add_circle(level, r, center._x, center._y, color=color, fill=fill)
        elif cicle is not None:
            dlog.add_circle(level, cicle.radius(), cicle.center().x(), cicle.center().y(), fill=fill, color=color)

    @staticmethod
    def add_point(level: Level.LEVEL_ANY,
                  x: float = None,
                  y: float = None,
                  pos: Vector2D = None,
                  color: Color = Color(string='red')):
        if x is not None:
            dlog._commands += f"{dlog._time} {level.value} p {x} {y} {color}"
        elif pos is not None:
            dlog.add_point(level, pos.x(), pos.y(), color=color)

    @staticmethod
    def add_message(level: Level.LEVEL_ANY,
                    x,
                    y,
                    msg):
        dlog._commands += f"{dlog._time} {level.value} m {round(x, 4)} {round(y, 4)} {msg}\n"

    # {color}\n
    @staticmethod
    def flush():
        if dlog._time is None or dlog._time.cycle() == 0:
            return
        dlog.debug(dlog._commands)
        dlog._commands = ""
