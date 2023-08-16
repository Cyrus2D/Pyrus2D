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
        self.pos_count_thr: Union[None, int] = 10
        self.relation_pos_count_thr: Union[None, int] = 5
        self.vel_count_thr: Union[None, int] = 10

        self.lost_count: int = 1000
        
        if string is None:
            return
        self.init_str(string)

    def init_str(self, string: str):
        data = string.split(" ")
        self.pos = Vector2D(float(data[0]), float(data[1]))
        self.seen_pos = Vector2D(float(data[0]), float(data[1]))
        self.vel = Vector2D(float(data[2]), float(data[3]))
        self.seen_vel = Vector2D(float(data[2]), float(data[3]))
        self.pos_count = 0
        self.seen_pos_count = 0
        self.rpos_count = 0
        self.vel_count = 0
        self.seen_vel_count = 0
        self.ghost_count = 0

    def inertia_point(self, cycle: int) -> Vector2D:
        return inertia_n_step_point(self.pos,
                                    self.vel,
                                    cycle,
                                    ServerParam.i().ball_decay())

    def inertia_final_point(self):
        return inertia_final_point(self.pos,
                                   self.vel,
                                   ServerParam.i().ball_decay())

    def copy(self):
        ball = BallObject()
        ball.pos = self.pos.copy()
        ball.vel = self.vel.copy()
        ball.rpos = self.rpos.copy()
        ball.seen_pos = self.seen_pos.copy()
        ball.seen_vel = self.seen_vel.copy()
        ball.heard_pos = self.heard_pos.copy()
        ball.heard_vel = self.heard_vel.copy()
        ball.dist_from_self = self.dist_from_self
        ball.angle_from_self = self.angle_from_self

        ball.pos_count = self.pos_count
        ball.vel_count = self.vel_count
        ball.ghost_count = self.ghost_count
        ball.seen_pos_count = self.seen_pos_count
        ball.rpos_count = self.rpos_count
        ball.heard_pos_count = self.heard_pos_count
        ball.heard_vel_count = self.heard_vel_count
        ball.lost_count = self.lost_count
        ball.seen_vel_count = self.seen_vel_count

        return ball

    def update_by_last_cycle(self, act: 'ActionEffector', game_mode: GameMode):
        SP = ServerParam.i()

        new_vel = Vector2D(0, 0)
        if self.vel_valid():
            new_vel = self.vel
            if act.last_body_command() == CommandType.KICK:
                accel = act.get_kick_info()
                log.sw_log().world().add_text(f"ESTIMATING BALL VEL WITH KICK ACTION")
                log.sw_log().world().add_text(f"accel={accel}, ball accel max={SP.ball_accel_max()}")
                if accel.r() > SP.ball_accel_max():
                    accel.set_length(SP.ball_accel_max())
                new_vel += accel
                self.vel_count = 0
            
            if new_vel.r() > SP.ball_speed_max():
                new_vel.set_length(SP.ball_speed_max())
        
        if (game_mode.type() == GameModeType.PlayOn
                or game_mode.type().is_goal_kick()
                or game_mode.type().is_goalie_catch_ball()
                or game_mode.type().is_penalty_taken()):
            self.pos_count = min(1000, self.pos_count + 1)
        else:
            if (self.pos_count >= 5 or (self.rpos_count >= 2
                                         and self.dist_from_self * 1.05 < SP.visible_distance())):
                self.pos_count = 1000
            else:
                self.pos_count = 1
            
            new_vel.assign(0, 0)
            self.vel_count = 0
            self.seen_vel.assign(0, 0)
            self.seen_vel_count = 0
        
        if self.pos_valid():
            self.pos += new_vel
        
        self.vel = new_vel
        self.vel *= SP.ball_decay()
        
        self.rpos_count = min(1000, self.rpos_count + 1)
        self.seen_pos_count = min(1000, self.seen_pos_count + 1)
        self.heard_pos_count = min(1000, self.heard_pos_count + 1)
        self.vel_count = min(1000, self.vel_count + 1)
        self.seen_vel_count = min(1000, self.seen_vel_count + 1)
        self.heard_vel_count = min(1000, self.heard_vel_count + 1)
        self.lost_count = min(1000, self.lost_count + 1)
    
    def update_only_vel(self, vel: Vector2D, vel_err: Vector2D, vel_count:int):
        self.vel = vel.copy()
        self.vel_error = vel_err.copy()
        self.vel_count = vel_count
        self.seen_vel = vel.copy()
        self.seen_vel_count = vel_count
    
    def update_only_relative_pos(self, rpos: Vector2D, rpos_err: Vector2D):
        self.rpos = rpos.copy()
        self.rpos_error = rpos_err.copy()
        self.rpos_count = 0
        self.seen_rpos = rpos.copy()
    
    def update_pos(self,
                   pos: Vector2D,
                   pos_err: Vector2D,
                   pos_count: int,
                   rpos: Vector2D,
                   rpos_err: Vector2D):
        self.pos = pos.copy()
        self.pos_error = pos_err.copy()
        self.pos_count = pos_count
        self.seen_pos = pos.copy()
        self.seen_pos_count = 0
        
        self.update_only_relative_pos(rpos, rpos_err)
        
        self.lost_count = 0
        self.ghost_count = 0
    
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
        
        self.vel = Vector2D(0, 0)
        self.vel_count = 0
        self.seen_vel = Vector2D(0,0)
        self.seen_vel_count = 0
        
        if type.is_goalie_catch_ball():
            return
        
        if type.is_corner_kick():
            if self.pos_count <= 1 and self.rpos.r2() > 3 ** 2:
                self.pos.assign(
                    (SP.pitch_half_length() - SP.corner_kick_margin()) * (1 if self.pos.x() > 0 else -1),
                    (SP.pitch_half_width() - SP.corner_kick_margin()) * (1 if self.pos.y() > 0 else -1)
                )
            return
        
        if type.is_kick_in():
            if self.pos_count <= 1 and self.rpos.r2() > 3**2:
                self.pos._y = SP.pitch_half_width() * (1 if self.pos._y > 0 else -1)
            return
        
        if type in [GMT.BeforeKickOff, GMT.KickOff_Left, GMT.KickOff_Right]:
            self.pos.assign(0,0)
            self.pos_count = 0
            self.seen_pos.assign(0, 0)
            self.seen_pos_count = 0
            self.ghost_count = 0


    def update_self_related(self, player: 'SelfObject' , prev: 'BallObject'):
        if self.rpos_count == 0:
            self.dist_from_self = self.rpos.r()
            self.angle_from_self = self.rpos.th()
        else:
            if prev.rpos.is_valid() and player.last_move().is_valid():
                self.rpos = prev.rpos + self.vel / ServerParam.i().ball_decay() - player.last_move()
            
            if self.rpos.is_valid() and self.pos_count > self.rpos_count:
                self.pos = player.pos + self.rpos
                self.dist_from_self = self.rpos.r()
                self.angle_from_self = self.rpos.th()
            elif self.pos_valid() and player.pos_valid():
                self.rpos = self.pos - player.pos
                self.dist_from_self = self.rpos.r()
                self.angle_from_self = self.rpos.th()
            else:
                self.dist_from_self = 1000
                self.angle_from_self = AngleDeg(0)
    
    def update_by_hear(self,
                       act: 'ActionEffector',
                       sender_to_ball_dist: float,
                       heard_pos: Vector2D,
                       heard_vel: Vector2D,
                       is_pass: bool = False):
        if BallObject.DEBUG:
            log.sw_log().sensor().add_text( f"(update ball by hear) prior_pos={self.pos} new_pos={heard_pos}")
            log.sw_log().sensor().add_text( f"(update ball by hear) prior_vel={self.vel} new_pos={heard_vel}")

        self.heard_pos =heard_pos.copy()
        self.heard_vel = heard_vel.copy()
        self.heard_pos_count = 0
        self.heard_vel_count = 0
        
        if act.last_body_command() == CommandType.KICK:
            return
        
        dist_diff = heard_pos.dist(self.pos)
        if is_pass and heard_vel.is_valid() and self.seen_vel_count > 0:
            if self.seen_pos_count > 0:
                self.pos = heard_pos.copy()
                self.pos_count = 1
            self.vel = heard_vel.copy()
            self.vel_count = 1
            return
        
        if (self.ghost_count == 1 and self.pos_count == 1 and dist_diff < 3) or self.ghost_count > 1:
            self.pos = heard_pos.copy()
            self.pos_count = 1
            
            if heard_vel.is_valid():
                self.vel = heard_vel.copy()
                self.vel_count =1
            return
        
        if self.pos_count >= 5 or (self.pos_count >= 2
                                     and (dist_diff > sender_to_ball_dist *0.05 + 1
                                          or sender_to_ball_dist < self.dist_from_self *0.95)):
            self.pos = heard_pos.copy()
            self.pos_count = 1
            
            if heard_vel.is_valid():
                self.vel = heard_vel.copy()
                self.vel_count =1
            return
        
        if self.pos_count > 0 and sender_to_ball_dist+ 1 < ServerParam.i().visible_distance() < self.dist_from_self:
            self.pos = heard_pos.copy()
            self.pos_count = 1
            
            if heard_vel.is_valid():
                self.vel = heard_vel.copy()
                self.vel_count =1
            return
    
    def set_ghost(self):
        if self.ghost_count > 0:
            self.pos_count = 1000
            self.rpos_count = 1000
            self.lost_count = 0
            self.ghost_count += 1
            
            self.dist_from_self = 1000
        else:
            self.ghost_count = 1

    def __str__(self):
        return f'''Ball pos: {self.pos} vel:{self.vel}'''
