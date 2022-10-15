from lib.math.soccer_math import *
from lib.player.action_effector import ActionEffector
from lib.player.object import *
from lib.player_command.player_command import CommandType
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType


# from lib.player.templates import *


class BallObject(Object):
    VEL_COUNT_THR = 10
    POS_COUNT_THR = 10
    RPOS_COUNT_THR = 5

    def __init__(self, string=None):
        super().__init__()
        self._dist_from_self: float = 10000
        self._angle_from_self = AngleDeg(0.0)
        self._pos = Vector2D.invalid()
        self._vel = Vector2D.invalid()
        
        self._rpos_count:int = 1000
        self._heard_pos_count: int = 1000
        self._heard_vel_count: int = 1000
        self._lost_count: int = 1000
        
        if string is None:
            return
        self.init_str(string)

    def init_str(self, string: str):
        data = string.split(" ")
        self._pos = Vector2D(float(data[0]), float(data[1]))
        self._vel = Vector2D(float(data[2]), float(data[3]))

    def _update_more_with_full_state(self, wm):
        self._dist_from_self = wm.self().pos().dist(self._pos)
        self._angle_from_self = (wm.self().pos() - self._pos).th()

    def dist_from_self(self):
        return self._dist_from_self

    def angle_from_self(self):
        return self._angle_from_self

    def vel_valid(self):
        return self.vel_count() < BallObject.VEL_COUNT_THR

    def pos_valid(self):
        return self.pos_count() < BallObject.POS_COUNT_THR

    def __repr__(self):
        return f"(pos: {self.pos()}) (vel:{self.vel()})"

    def inertia_point(self, cycle: int) -> Vector2D:
        return inertia_n_step_point(self._pos,
                                    self._vel,
                                    cycle,
                                    ServerParam.i().ball_decay())

    def inertia_final_point(self):
        return inertia_final_point(self.pos(),
                                   self.vel(),
                                   ServerParam.i().ball_decay())

    def copy(self):
        ball = BallObject()
        
        ball._dist_from_self = self._dist_from_self
        ball._angle_from_self = self._angle_from_self
        ball._pos = self._pos
        ball._vel = self._vel

        return ball

    def update(self, act: ActionEffector, game_mode: GameMode):
        SP = ServerParam.i()

        new_vel = Vector2D(0, 0)
        if self.velValid():
            accel: Vector2D = Vector2D(0,0)
            new_vel = self.vel()
            
            if act.last_body_command() == CommandType.KICK:
                accel = act.get_kick_info()
                
                if accel.r() > SP.ball_accel_max():
                    accel.set_length(SP.ball_accel_max())
                new_vel += accel
            
            if new_vel.r() > SP.ball_speed_max():
                new_vel.set_length(SP.ball_speed_max())
        
        if (game_mode.type() == GameModeType.PlayOn
                or game_mode.type().is_goal_kick()
                or game_mode.type().is_goalie_catch_ball()
                or game_mode.type().is_penalty_taken()):
            self._pos_count = min(1000, self._pos_count + 1)
        else:
            if (self._pos_count >= 5 or (self._rpos_count >= 2
                                         and self.dist_from_self() * 1.05 < SP.visible_distance())):
                self._pos_count = 1000
            else:
                self._pos_count = 1
            
            new_vel.assign(0,0)
            self._vel_count = 0
            self._seen_vel.assign(0,0)
            self._seen_vel_count = 0
        
        if self.pos_valid():
            self._pos += new_vel
        
        self._vel = new_vel
        self._vel *= SP.ball_decay()
        
        self._rpos_count = min(1000, self._rpos_count + 1)
        self._seen_pos_count = min(1000, self._seen_pos_count + 1)
        self._heard_pos_count = min(1000, self._heard_pos_count + 1)
        self._vel_count = min(1000, self._vel_count + 1)
        self._seen_vel_count = min(1000, self._seen_vel_count + 1)
        self._heard_vel_count = min(1000, self._heard_vel_count + 1)
        self._lost_count = min(1000, self._lost_count + 1)