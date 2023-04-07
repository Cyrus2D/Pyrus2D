from typing import Union

from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.vector_2d import Vector2D
from lib.rcsc.game_time import GameTime


class MessengerMemory:
    class Player:
        def __init__(self,
                     sender:int=0,
                     unum:int=0,
                     pos:Vector2D=Vector2D(),
                     body:float=-360,
                     stamina:float=-1) -> None:
            self.sender_: int = sender
            self.pos_: Vector2D = pos.copy()
            self.unum_: int = unum
            self.body_: float = body
            self.stamina_: float = stamina

    class Ball:
        def __init__(self, sender=0, pos: Vector2D = Vector2D(), vel: Vector2D = None) -> None:
            self.sender_: int = sender
            self.pos_: Vector2D = pos.copy()
            self.vel_: Vector2D = vel.copy()

    class Goalie:
        def __init__(self, sender = 0, pos: Vector2D = Vector2D(), body: AngleDeg = None):
            self.sender_ = sender
            self.pos_ = pos.copy()
            self.body_ = body.copy()

    class Pass:
        def __init__(self, sender: int, receiver: int, pos: Vector2D):
            self._sender = sender
            self._receiver = receiver
            self._pos = pos.copy()

    class Stamina:
        def __init__(self, sender: int, rate: float):
            self.rate_ = rate
            self.sender_ = sender


    class Recovery:
        def __init__(self, sender: int, rate: float):
            self.rate_ = rate
            self.sender_ = sender

    def __init__(self) -> None:
        self._time: GameTime = GameTime()

        self._players: list[MessengerMemory.Player] = []
        self._player_time: GameTime = GameTime()

        self._balls: list[MessengerMemory.Ball] = []
        self._ball_time: GameTime = GameTime()

        self._pass: list[MessengerMemory.Pass] = []
        self._pass_time: GameTime = GameTime()

        self._goalie: list[MessengerMemory.Goalie] = []
        self._goalie_time: GameTime = GameTime()

        self._player_record: list[tuple[GameTime, MessengerMemory.Player]] = []

        self._stamina: list[MessengerMemory.Stamina] = []
        self._stamina_time: GameTime = GameTime()

        self._recovery: list[MessengerMemory.Recovery] = []
        self._recovery_time: GameTime = GameTime()

    def add_ball(self, sender: int, pos: Vector2D, vel: Vector2D, current_time: GameTime):
        if self._ball_time != current_time:
            self._balls.clear()

        self._balls.append(MessengerMemory.Ball(sender, pos, vel))
        self._ball_time = current_time.copy()
        self._time = current_time.copy()

    def add_player(self,
                   sender: int,
                   unum: int,
                   pos: Vector2D,
                   current_time: GameTime,
                   body: float = -360.,
                   stamina: float = -1.):
        if self._player_time != current_time:
            self._players.clear()

        self._players.append(MessengerMemory.Player(sender, unum, pos, body, stamina))
        self._player_time = current_time.copy()

        self._player_record.append((current_time, self._players[-1]))
        if len(self._player_record) > 30:
            self._player_record = self._player_record[1:]

        self._time = current_time.copy()

    def add_pass(self, sender: int, receiver: int, pos: Vector2D, current: GameTime):
        if self._pass_time != current:
            self._pass.clear()

        self._pass.append(MessengerMemory.Pass(sender, receiver, pos))
        self._pass_time = current.copy()

        self._time = current.copy()

    def add_opponent_goalie(self, sender:int, pos: Vector2D, current_time: GameTime, body: Union[AngleDeg, float]):
        if self._goalie_time != current_time:
            self._goalie.clear()

        self._goalie.append(MessengerMemory.Goalie(sender, pos, AngleDeg(body)))
        self._goalie_time = current_time.copy()

        self._time = current_time.copy()

    def add_stamina(self, sender: int, rate: float, current_time: GameTime):
        if self._stamina_time != current_time:
            self._stamina.clear()

        self._stamina.append(MessengerMemory.Stamina(sender, rate))
        self._stamina_time = current_time.copy()

        self._time = current_time.copy()

    def add_recovery(self, sender: int, rate: float, current_time: GameTime):
        if self._recovery_time != current_time:
            self._recovery.clear()

        self._recovery.append(MessengerMemory.Recovery(sender, rate))
        self._recovery_time = current_time.copy()

        self._time = current_time.copy()

    def goalie_time(self):
        return self._goalie_time

    def time(self):
        return self._time

    def players(self):
        return self._players

    def player_time(self):
        return self._player_time

    def balls(self):
        return self._balls

    def ball_time(self):
        return self._ball_time

    def pass_time(self):
        return self._pass_time

    def pass_(self):
        return self._pass

    def player_record(self):
        return self._player_record

    def goalie(self):
        return self._goalie

    def recovery(self):
        return self._recovery

    def recovery_time(self):
        return self._recovery_time

    def stamina(self):
        return self._stamina

    def stamina_time(self):
        return self._stamina_time



