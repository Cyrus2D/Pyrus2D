from pyrusgeom.vector_2d import Vector2D
from lib.rcsc.game_time import GameTime


class MessengerMemory:
    class Object:
        def __init__(self, sender = 0, pos: Vector2D = Vector2D(), vel: Vector2D = None) -> None:
            self.sender_: int = sender
            self.pos_: Vector2D = pos
            self.vel_: Vector2D = vel

    class Player(Object):
        def __init__(self,
                     sender:int=0,
                     unum:int=0,
                     pos:Vector2D=Vector2D(),
                     vel: Vector2D = None,
                     body:float=-360,
                     stamina:float=-1) -> None:
            super().__init__(sender, pos, vel)
            self.unum_: int = unum
            self.body_: float = body
            self.stamina_: float = stamina
    
    class Ball(Object):
        def __init__(self, sender=0, pos: Vector2D = Vector2D(), vel: Vector2D = None) -> None:
            super().__init__(sender, pos, vel)

    class Pass:
        def __init__(self, sender: int, receiver: int, pos: Vector2D):
            self._sender = sender
            self._receiver = receiver
            self._pos = pos.copy()

    def __init__(self) -> None:
        self._time: GameTime = GameTime()

        self._players: list[MessengerMemory.Player] = []
        self._player_time: GameTime = GameTime()
        
        self._balls: list[MessengerMemory.Ball] = []
        self._ball_time: GameTime = GameTime()

        self._pass: list[MessengerMemory.Pass] = []
        self._pass_time: GameTime = GameTime()

        self._player_record: list[tuple[GameTime, MessengerMemory.Player]] = []

    def add_ball(self, sender: int, pos: Vector2D, vel: Vector2D, current_time: GameTime):
        if self._ball_time != current_time:
            self._balls.clear()

        self._balls.append(MessengerMemory.Ball(sender, pos, vel))
        self._ball_time = current_time.copy()
        self._time = current_time.copy()
    
    def add_player(self, sender: int, unum: int, pos: Vector2D, current_time: GameTime):
        if self._player_time != current_time:
            self._players.clear()

        self._players.append(MessengerMemory.Player(sender, unum, pos))
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
    
    