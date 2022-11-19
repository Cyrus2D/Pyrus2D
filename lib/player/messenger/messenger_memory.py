from lib.math.vector_2d import Vector2D
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
    
    def __init__(self) -> None:
        self._time: GameTime = GameTime()

        self._players: list[MessengerMemory.Player] = []
        self._player_time: GameTime = GameTime()
        
        self._balls: list[MessengerMemory.Player] = []
        self._ball_time: GameTime = GameTime()
        
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

        self._time = current_time.copy()
    
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
        

    
    