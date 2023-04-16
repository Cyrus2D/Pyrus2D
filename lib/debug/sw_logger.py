from pyrusgeom.circle_2d import Circle2D
from pyrusgeom.vector_2d import Vector2D

from lib.debug.color import Color
from lib.debug.level import Level
from lib.rcsc.game_time import GameTime


class SoccerWindow_Logger:
    class LoggerLevel:
        def __init__(self, level: Level, game_time: GameTime):
            self.level: Level = level
            self._time: GameTime = game_time
            self._commands = ""

        def add_line(self,
                     x1: float = None,
                     y1: float = None,
                     x2: float = None,
                     y2: float = None,
                     start: Vector2D = None,
                     end: Vector2D = None,
                     color: Color = Color(string="red")):
            if x1 is not None:
                self._commands += f"{self._time.cycle()},{self._time.stopped_cycle()} {self.level.value} l {x1} {y1} {x2} {y2} {color}\n"
            elif start is not None:
                self.add_line(start.x(), start.y(), end.x(), end.y(), color=color)

        def add_text(self, message: str = ""):
            self._commands += f"{self._time.cycle()},{self._time.stopped_cycle()} {self.level.value} M {message}\n"  # TODO flush if message size is so large like 8192 and bigger

        def add_circle(self,
                       r: float = None,
                       cx: float = None,
                       cy: float = None,
                       center: Vector2D = None,
                       circle: Circle2D = None,
                       fill: bool = False,
                       color: Color = Color(string='red'), ):
            if cx is not None:
                self._commands += f"{self._time.cycle()},{self._time.stopped_cycle()} {self.level.value} {'C' if fill else 'c'} {cx} {cy} {r} {color}\n"
            elif center is not None:
                self.add_circle(r, center.x(), center.y(), color=color, fill=fill)
            elif circle is not None:
                self.add_circle(circle.radius(), circle.center().x(), circle.center().y(), fill=fill,
                                color=color)

        def add_point(self,
                      x: float = None,
                      y: float = None,
                      pos: Vector2D = None,
                      color: Color = Color(string='red')):
            if x is not None:
                self._commands += f"{self._time.cycle()},{self._time.stopped_cycle()} {self.level.value} p {x} {y} {color}"
            elif pos is not None:
                self.add_point(pos.x(), pos.y(), color=color)

        def add_message(self,
                        x,
                        y,
                        msg):
            self._commands += f"{self._time.cycle()},{self._time.stopped_cycle()} {self.level.value} m {round(x, 4)} {round(y, 4)} {msg}\n"

    def __init__(self, team_name: str, unum: int, time: GameTime):
        self._file = open(f"/tmp/{team_name}-{unum}.log", 'w')
        self._time: GameTime = time

        self._system = SoccerWindow_Logger.LoggerLevel(Level.SYSTEM, self._time)
        self._sensor = SoccerWindow_Logger.LoggerLevel(Level.SENSOR, self._time)
        self._world = SoccerWindow_Logger.LoggerLevel(Level.WORLD, self._time)
        self._action = SoccerWindow_Logger.LoggerLevel(Level.ACTION, self._time)
        self._intercept = SoccerWindow_Logger.LoggerLevel(Level.INTERCEPT, self._time)
        self._kick = SoccerWindow_Logger.LoggerLevel(Level.KICK, self._time)
        self._hold = SoccerWindow_Logger.LoggerLevel(Level.HOLD, self._time)
        self._dribble = SoccerWindow_Logger.LoggerLevel(Level.DRIBBLE, self._time)
        self._pass = SoccerWindow_Logger.LoggerLevel(Level.PASS, self._time)
        self._cross = SoccerWindow_Logger.LoggerLevel(Level.CROSS, self._time)
        self._shoot = SoccerWindow_Logger.LoggerLevel(Level.SHOOT, self._time)
        self._clear = SoccerWindow_Logger.LoggerLevel(Level.CLEAR, self._time)
        self._block = SoccerWindow_Logger.LoggerLevel(Level.BLOCK, self._time)
        self._mark = SoccerWindow_Logger.LoggerLevel(Level.MARK, self._time)
        self._positioning = SoccerWindow_Logger.LoggerLevel(Level.POSITIONING, self._time)
        self._role = SoccerWindow_Logger.LoggerLevel(Level.ROLE, self._time)
        self._team = SoccerWindow_Logger.LoggerLevel(Level.TEAM, self._time)
        self._communication = SoccerWindow_Logger.LoggerLevel(Level.COMMUNICATION, self._time)
        self._analyzer = SoccerWindow_Logger.LoggerLevel(Level.ANALYZER, self._time)
        self._action_chain = SoccerWindow_Logger.LoggerLevel(Level.ACTION_CHAIN, self._time)
        self._plan = SoccerWindow_Logger.LoggerLevel(Level.PLAN, self._time)
        self._training = SoccerWindow_Logger.LoggerLevel(Level.TRAINING, self._time)
        self._any = SoccerWindow_Logger.LoggerLevel(Level.LEVEL_ANY, self._time)

        self._levels: list[SoccerWindow_Logger.LoggerLevel] = [
            self._system,
            self._sensor,
            self._world,
            self._action,
            self._intercept,
            self._kick,
            self._hold,
            self._dribble,
            self._pass,
            self._cross,
            self._shoot,
            self._clear,
            self._block,
            self._mark,
            self._positioning,
            self._role,
            self._team,
            self._communication,
            self._analyzer,
            self._action_chain,
            self._plan,
            self._training,
            self._any
        ]

    def flush(self):
        if self._time is None or self._time.cycle() == 0:
            return
        for l in self._levels:
            self._file.write(l._commands)
            l._commands = ""

    def update_time(self, t: GameTime):
        self._time.assign(t.cycle(), t.stopped_cycle())

    def system(self):
        return self._system

    def sensor(self):
        return self._sensor

    def world(self):
        return self._world

    def action(self):
        return self._action

    def intercept(self):
        return self._intercept

    def kick(self):
        return self._kick

    def hold(self):
        return self._hold

    def dribble(self):
        return self._dribble

    def pass_(self):
        return self._pass

    def cross(self):
        return self._cross

    def shoot(self):
        return self._shoot

    def clear(self):
        return self._clear

    def block(self):
        return self._block

    def mark(self):
        return self._mark

    def positioning(self):
        return self._positioning

    def role(self):
        return self._role

    def team(self):
        return self._team

    def communication(self):
        return self._communication

    def analyzer(self):
        return self._analyzer

    def action_chain(self):
        return self._action_chain

    def plan(self):
        return self._plan

    def training(self):
        return self._training

    def any(self):
        return self._any