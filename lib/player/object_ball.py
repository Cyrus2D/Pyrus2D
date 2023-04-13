from lib.debug.debug import log
from lib.debug.level import Level
from pyrusgeom.soccer_math import *
from lib.player.object import *
from lib.player_command.player_command import CommandType
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.object_self import SelfObject
    from lib.player.object_ball import BallObject
    from lib.player.action_effector import ActionEffector


class BallObject(Object):
    DEBUG = True

    def __init__(self, string=None):
        super().__init__()
        self._pos_count_thr: Union[None, int] = 10
        self._relation_pos_count_thr: Union[None, int] = 5
        self._vel_count_thr: Union[None, int] = 10

        self._lost_count: int = 1000
        
        if string is None:
            return
        self.init_str(string)

    def init_str(self, string: str):
        data = string.split(" ")
        self._pos = Vector2D(float(data[0]), float(data[1]))
        self._seen_pos = Vector2D(float(data[0]), float(data[1]))
        self._vel = Vector2D(float(data[2]), float(data[3]))
        self._seen_vel = Vector2D(float(data[2]), float(data[3]))
        self._pos_count = 0
        self._seen_pos_count = 0
        self._rpos_count = 0
        self._vel_count = 0
        self._seen_vel_count = 0
        self._ghost_count = 0

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
        ball._pos = self._pos.copy()
        ball._vel = self._vel.copy()
        ball._rpos = self._rpos.copy()
        ball._seen_pos = self._seen_pos.copy()
        ball._seen_vel = self._seen_vel.copy()
        ball._heard_pos = self._heard_pos.copy()
        ball._heard_vel = self._heard_vel.copy()
        ball._dist_from_self = self._dist_from_self
        ball._angle_from_self = self._angle_from_self

        ball._pos_count = self.pos_count()
        ball._vel_count = self.vel_count()
        ball._ghost_count = self.ghost_count()
        ball._seen_pos_count = self.seen_pos_count()
        ball._rpos_count = self.rpos_count()
        ball._heard_pos_count = self.heard_pos_count()
        ball._heard_vel_count = self.heard_vel_count()
        ball._lost_count = self.lost_count()
        ball._seen_vel_count = self.seen_vel_count()

        return ball

    def update_by_last_cycle(self, act: 'ActionEffector', game_mode: GameMode):
        SP = ServerParam.i()

        new_vel = Vector2D(0, 0)
        if self.vel_valid():
            new_vel = self.vel()
            if act.last_body_command() == CommandType.KICK:
                accel = act.get_kick_info()
                log.sw_log().world().add_text(f"ESTIMATING BALL VEL WITH KICK ACTION")
                log.sw_log().world().add_text(f"accel={accel}, ball accel max={SP.ball_accel_max()}")
                if accel.r() > SP.ball_accel_max():
                    accel.set_length(SP.ball_accel_max())
                new_vel += accel
                self._vel_count = 0
            
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
            
            new_vel.assign(0, 0)
            self._vel_count = 0
            self._seen_vel.assign(0, 0)
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
    
    def update_only_vel(self, vel: Vector2D, vel_err: Vector2D, vel_count:int):
        self._vel = vel.copy()
        self._vel_error = vel_err.copy()
        self._vel_count = vel_count
        self._seen_vel = vel.copy()
        self._seen_vel_count = vel_count
    
    def update_only_relative_pos(self, rpos: Vector2D, rpos_err: Vector2D):
        self._rpos = rpos.copy()
        self._rpos_error = rpos_err.copy()
        self._rpos_count = 0
        self._seen_rpos = rpos.copy()
    
    def update_pos(self,
                   pos: Vector2D,
                   pos_err: Vector2D,
                   pos_count: int,
                   rpos: Vector2D,
                   rpos_err: Vector2D):
        self._pos = pos.copy()
        self._pos_error = pos_err.copy()
        self._pos_count = pos_count
        self._seen_pos = pos.copy()
        self._seen_pos_count = 0
        
        self.update_only_relative_pos(rpos, rpos_err)
        
        self._lost_count = 0
        self._ghost_count = 0
    
    def update_all(self, 
                   pos: Vector2D,
                   pos_err: Vector2D,
                   pos_count: int,
                   rpos: Vector2D,
                   rpos_err: Vector2D,
                   vel: Vector2D,
                   vel_err: Vector2D,
                   vel_count: int):
        self.update_pos(pos, pos_err, pos_count, rpos, rpos_err)
        self.update_only_vel(vel, vel_err, vel_count)

    def update_by_game_mode(self, game_mode: GameMode):
        SP = ServerParam.i()
        GMT = GameModeType
        type = game_mode.type()
        
        if type in [GMT.PlayOn,
                    GMT.GoalKick_Left,
                    GMT.GoalKick_Right,
                    GMT.PenaltyTaken_Left,
                    GMT.PenaltyTaken_Right]:
            return
        
        self._vel = Vector2D(0, 0)
        self._vel_count = 0
        self._seen_vel = Vector2D(0,0)
        self._seen_vel_count = 0
        
        if type.is_goalie_catch_ball():
            return
        
        if type.is_corner_kick():
            if self.pos_count() <= 1 and self.rpos().r2() > 3 ** 2:
                self._pos.assign(
                    (SP.pitch_half_length() - SP.corner_kick_margin()) * (1 if self.pos().x() > 0 else -1),
                    (SP.pitch_half_width() - SP.corner_kick_margin()) * (1 if self.pos().y() > 0 else -1)
                )
            return
        
        if type.is_kick_in():
            if self.pos_count() <= 1 and self.rpos().r2() > 3**2:
                self._pos._y = SP.pitch_half_width() * (1 if self.pos().y() > 0 else -1)
            return
        
        if type in [GMT.BeforeKickOff, GMT.KickOff_Left, GMT.KickOff_Right]:
            self._pos.assign(0,0)
            self._pos_count = 0
            self._seen_pos.assign(0, 0)
            self._seen_pos_count = 0
            self._ghost_count = 0


    def update_self_related(self, player: 'SelfObject' , prev: 'BallObject'):
        if self.rpos_count() == 0:
            self._dist_from_self = self.rpos().r()
            self._angle_from_self = self.rpos().th()
        else:
            if prev.rpos().is_valid() and player.last_move().is_valid():
                self._rpos = prev.rpos() + self.vel() / ServerParam.i().ball_decay() - player.last_move()
            
            if self.rpos().is_valid() and self.pos_count() > self.rpos_count():
                self._pos = player.pos() + self.rpos()
                self._dist_from_self = self.rpos().r()
                self._angle_from_self = self.rpos().th()
            elif self.pos_valid() and player.pos_valid():
                self._rpos = self.pos() - player.pos()
                self._dist_from_self = self.rpos().r()
                self._angle_from_self = self.rpos().th()
            else:
                self._dist_from_self = 1000
                self._angle_from_self = AngleDeg(0)
    
    def update_by_hear(self,
                       act: 'ActionEffector',
                       sender_to_ball_dist: float,
                       heard_pos: Vector2D,
                       heard_vel: Vector2D,
                       is_pass: bool = False):
        if BallObject.DEBUG:
            log.sw_log().sensor().add_text( f"(update ball by hear) prior_pos={self.pos()} new_pos={heard_pos}")
            log.sw_log().sensor().add_text( f"(update ball by hear) prior_vel={self.vel()} new_pos={heard_vel}")

        self._heard_pos =heard_pos.copy()
        self._heard_vel = heard_vel.copy()
        self._heard_pos_count = 0
        self._heard_vel_count = 0
        
        if act.last_body_command() == CommandType.KICK:
            return
        
        dist_diff = heard_pos.dist(self.pos())
        if is_pass and heard_vel.is_valid() and self.seen_vel_count() > 0:
            if self.seen_pos_count() > 0:
                self._pos = heard_pos.copy()
                self._pos_count = 1
            self._vel = heard_vel.copy()
            self._vel_count = 1
            return
        
        if (self._ghost_count == 1 and self.pos_count() == 1 and dist_diff < 3) or self.ghost_count() > 1:
            self._pos = heard_pos.copy()
            self._pos_count = 1
            
            if heard_vel.is_valid():
                self._vel = heard_vel.copy()
                self._vel_count =1
            return
        
        if self.pos_count() >= 5 or (self.pos_count() >= 2
                                     and (dist_diff > sender_to_ball_dist *0.05 + 1
                                          or sender_to_ball_dist < self._dist_from_self *0.95)):
            self._pos = heard_pos.copy()
            self._pos_count = 1
            
            if heard_vel.is_valid():
                self._vel = heard_vel.copy()
                self._vel_count =1
            return
        
        if self.pos_count() > 0 and sender_to_ball_dist+ 1 < ServerParam.i().visible_distance() < self.dist_from_self():
            self._pos = heard_pos.copy()
            self._pos_count = 1
            
            if heard_vel.is_valid():
                self._vel = heard_vel.copy()
                self._vel_count =1
            return
    
    def set_ghost(self):
        if self._ghost_count > 0:
            self._pos_count = 1000
            self._rpos_count = 1000
            self._lost_count = 0
            self._ghost_count += 1
            
            self._dist_from_self = 1000
        else:
            self._ghost_count = 1

    def lost_count(self):
        return self._lost_count

    def __str__(self):
        return f'''Ball pos: {self.pos()} vel:{self.vel()}'''
