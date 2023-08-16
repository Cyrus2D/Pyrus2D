from typing import Union
from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.soccer_math import min_max
from pyrusgeom.vector_2d import Vector2D
from lib.debug.debug import log
from lib.player.action_effector import ActionEffector
from lib.player.object_ball import BallObject
from lib.player.object_player import PlayerObject
from lib.player.sensor.body_sensor import SenseBodyParser
from lib.player.stamina_model import StaminaModel
from lib.player_command.player_command import CommandType
from lib.rcsc.game_time import GameTime
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import SideID, ViewWidth


class SelfObject(PlayerObject):
    FACE_COUNT_THR = 5
    DEBUG = True
    
    def __init__(self, player: PlayerObject = None):
        super().__init__()

        self.time: GameTime = GameTime()
        self.sense_body_time: GameTime = GameTime()
        self.view_width: ViewWidth = ViewWidth.ILLEGAL
        self.neck: AngleDeg = AngleDeg(0)
        self.face_error = 0.5
        self.stamina_model: StaminaModel = StaminaModel()
        self.last_catch_time: GameTime = GameTime()
        self.tackle_expires: int = 0
        self.charge_expires: int = 0
        self.arm_moveable: int = 0
        self.arm_expires: int = 0
        self.pointto_rpos: Vector2D = Vector2D.invalid()
        self.pointto_pos: Vector2D = Vector2D.invalid()
        self.last_pointto_time: GameTime = GameTime()
        self.attentionto_side: SideID = SideID.NEUTRAL
        self.attentionto_unum: int = 0
        self.collision_estimated: bool = False
        self.collides_with_none: bool = False
        self.collides_with_ball: bool = False
        self.collides_with_player: bool = False
        self.collides_with_post: bool = False
        self.kickable: bool = False
        self.kick_rate: float = 0
        self.catch_probability: float = 0
        self.tackle_probability: float = 0
        self.foul_probability: float = 0
        self._last_move: Vector2D = Vector2D(0, 0)
        self.last_moves: list[Vector2D] = [Vector2D(0, 0) for _ in range(4)]
        self.arm_movable: int = 0
        self.face_count_thr: Union[None, int] = 5

    def init(self, side: SideID, unum: int, goalie: bool):
        self.side = side
        self.unum = unum
        self.goalie = goalie

    def update_by_player_info(self, player: PlayerObject):
        self.unum = player.unum
        self.pos = player.pos
        self.vel = player.vel
        self.side = player.side
        self.body = player.body
        self.neck = player.neck
        self.face = player.face
        self.goalie = player.goalie
        self.player_type_id = player.player_type_id
        self.player_type = player.player_type
        self.stamina_model = player.stamina_model
        self.kick = player.kick
        self.tackle = player.tackle
        self.charged = player.charged
        self.card = player.card
        self.card = player.card
        self.kick_rate = player.kick_rate
        self.rpos_count = 0
        self.vel_count = 0
        self.pos_count = 0
        self.body_count = 0
        self.change_focus_count = 0
        self.focus_point_dist = 0
        self.focus_point_dir = AngleDeg(0)
        self.ghost_count = 0

    def is_frozen(self):
        return self.tackle_expires > 0 or self.charge_expires > 0
    
    def face_valid(self):
        return self.face_count < SelfObject.FACE_COUNT_THR
    
    def last_move(self, index=None):
        if index:
            index = min_max(0, index, len(self.last_moves)-1)
            return self.last_moves[index] 
        return self.last_move
    
    def is_kicking(self):
        return self.kicking
    
    def is_kickable(self, buf=0.0):
        return self.kickable
    
    def set_view_mode(self, vw: ViewWidth):
        self.view_width = vw

    def update_by_last_cycle(self, act: ActionEffector, current_time: GameTime):
        if self.time == current_time:
            return
        
        SP = ServerParam.i()
        
        self.time = current_time.copy()
        self.kicking = False
        
        accel = Vector2D(0,0)
        dash_power = 0
        turn_moment = 0
        neck_moment = 0
        
        if act.last_body_command() == CommandType.DASH:
            accel, dash_power = act.get_dash_info()

        elif act.last_body_command() == CommandType.TURN:
            turn_moment = act.get_turn_info()

        elif act.last_body_command() == CommandType.TACKLE:
            if not act.tackle_foul():
                self.tackle_expires = SP.tackle_cycles()
            self.kicking = True

        elif act.last_body_command() == CommandType.MOVE:
            self.pos = act.get_move_pos()

        elif act.last_body_command() == CommandType.CATCH:
            pass
        
        elif act.last_body_command() == CommandType.KICK:
            self.kicking = True
        
        if act.done_turn_neck():
            neck_moment = act.get_turn_neck_moment()
        self.neck += min_max(SP.min_neck_angle(), neck_moment, SP.max_neck_angle())

        if act.done_change_focus():
            self.focus_point_dir += act.get_change_focus_moment_dir()
            self.focus_point_dist += act.get_change_focus_moment_dist()

        self.stamina_model.simulate_dash(self.player_type, dash_power)
        
        self.body += turn_moment
        self.face = self.body + self.neck
        self.face_error = 0.5

        if self.vel_valid():
            self.vel += accel
        if self.pos_valid():
            self.pos += self.vel
        self.vel *= self.player_type.player_decay()
        
        self.pos_count += 1
        self.seen_pos_count += 1
        self.vel_count += 1
        self.seen_vel_count += 1
        self.body_count += 1
        self.face_count += 1
        self.pointto_count = min(1000, self.pointto_count + 1)
        self.tackle_expires = max(0, self.tackle_expires - 1)
        self.charge_expires = max(0, self.charge_expires - 1)
        self.arm_movable = max(0, self.arm_movable - 1)
        self.arm_expires = max(0, self.arm_expires - 1)
        self.last_move = self.vel / self.player_type.player_decay()
        self.last_moves = [self.last_move] + self.last_moves[0:-1]
        self.collision_estimated = False
        self.collides_with_none = False
        self.collides_with_ball = False
        self.collides_with_player = False
        self.collides_with_post = False

    def update_angle_by_see(self, face: float, angle_face_error, current_time: GameTime):
        self.time = current_time.copy()
        self.face = AngleDeg(face)
        self.body = AngleDeg(face - self.neck.degree())
        self.face_error = angle_face_error
        self.body_count = 0
        self.face_count = 0
        
    def update_vel_dir_after_see(self, sense: SenseBodyParser, current_time: GameTime):
        if sense.time() != current_time:
            log.os_log().error("(update vel dir after see) sense time does not match current time")
            return
        
        if self.face_count == 0:
            sensed_speed_dir = sense.speed_dir()
            sensed_speed_dir_error = 0.5
            if sensed_speed_dir == 0.0:
                sensed_speed_dir_error = 1.0
            if sensed_speed_dir > 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir + 0.5)
            elif sensed_speed_dir < 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir - 0.5)

            vel_ang = self.face + sensed_speed_dir
            
            self.vel.set_polar(sense.speed_mag(), vel_ang)
            self.vel_count = 0
            self.seen_vel = self.vel.copy()
            self.seen_vel_count = 0

            # TODO cos_min_max and sin_min_max should be implemented
            # min_cos, max_cos = vel_ang.cos_min_max(self.face_error() + sensed_speed_dir_error)
            # min_sin, max_sin = vel_ang.sin_min_max(self.face_error() + sensed_speed_dir_error)
            # self.vel_error.assign((max_cos - min_cos) * (sense.speed_mag() + 0.005), (max_sin - min_sin) * (sense.speed_mag() + 0.005))

            if not self.collision_estimated:
                new_last_move = self.vel/self.player_type.player_decay()
                self.last_move.assign(new_last_move.x(), new_last_move.y())
    
    def update_pos_by_see(self, pos: Vector2D, pos_err: Vector2D, my_possible_posses: list[Vector2D], face: float, face_err: float, current_time: GameTime):
        self.time = current_time.copy()

        if self.pos_count == 1:
            new_pos = pos.copy()
            new_err = pos_err.copy()
            if self.pos_error.x() < pos_err.x():
                new_pos.set_x(pos.x() + (self.pos.x() - pos.x()) * (pos_err.x() / (self.pos_error.x() + pos_err.x())))
                new_err.set_x((self.pos_error.x() + pos_err.x()) * 0.5)
            if self.pos_error.y() < pos_err.y():
                new_pos.set_y(pos.y() + (self.pos.y() - pos.y()) * (pos_err.y() / (self.pos_error.y() + pos_err.y())))
                new_err.set_y((self.pos_error.y() + pos_err.y()) * 0.5)
            self.pos = new_pos.copy()
            self.pos_error = new_err.copy()
            self.possible_posses = [self.pos.copy()]
            # TODO has sensed collision -> collisionEstimated
            if self.seen_pos_count == 1 and (self.has_sensed_collision() or not self.last_move().is_valid()):
                self._last_move = new_pos - self.seen_pos
                self.last_moves[0] = self.last_move().copy()
        else:
            self.pos = pos.copy()
            self.pos_error = pos_err.copy()
            self.possible_posses = my_possible_posses

        self.seen_pos = pos.copy()
        self.face = AngleDeg(face)
        self.body = AngleDeg(face) - self.neck

        self.pos_count = 0
        self.seen_pos_count = 0
        self.body_count = 0
        self.face_count = 0
    
    def has_sensed_collision(self):
        return(
            self.collides_with_none
            or self.collides_with_ball
            or self.collides_with_player
            or self.collides_with_post
        )
    
    def update_self_after_sense_body(self, sense_body: SenseBodyParser, act: ActionEffector, current_time: GameTime):
        if self.sense_body_time == current_time:
            log.os_log().critical(f"(self update after see) called twice at {current_time}")
            return
        
        self.sense_body_time = current_time.copy()

        self.update_by_last_cycle(act, current_time)

        self.kicking = act.last_body_command() == CommandType.KICK or act.last_body_command() == CommandType.TACKLE
        self.view_width = sense_body.view_width()

        self.stamina_model.update_by_sense_body(sense_body.stamina(),
                                                 sense_body.effort(),
                                                 sense_body.stamina_capacity(),
                                                 current_time)
        
        if abs(self.neck.degree() - sense_body.neck_relative()) > 0.5:
            self.neck = AngleDeg(sense_body.neck_relative())
        
        if (sense_body.none_collided()
            or sense_body.ball_collided()
            or sense_body.player_collided()
            or sense_body.post_collided()):
            
            self.collision_estimated = False
            
            if sense_body.none_collided():
                self.collides_with_none = True
            if sense_body.ball_collided():
                self.collides_with_ball = True
                self.collision_estimated = True
            if sense_body.player_collided():
                self.collides_with_player = True
                self.collision_estimated = True
            if sense_body.post_collided():
                self.collides_with_post = True
                self.collision_estimated = True

        if self.face_valid():
            self.face = self.body + self.neck
            
            estimate_vel = self.vel.copy()
            sensed_speed_dir = sense_body.speed_dir()
            if sensed_speed_dir > 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir + 0.5)
            elif sensed_speed_dir < 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir - 0.5)
            
            vel_ang = self.face + sensed_speed_dir
            self.vel.set_polar(sense_body.speed_mag(), vel_ang)

            if (not self.has_sensed_collision()
                and self.vel_valid()
                and sense_body.speed_mag() < self.player_type.real_speed_max()*self.player_type.player_decay()*0.11):
                
                if (estimate_vel.r() > 0.01
                    and sense_body.speed_mag() < estimate_vel.r() *0.2
                    and (estimate_vel.abs_x() < 0.08 or estimate_vel.x() * self.vel.x() < 0)
                    and (estimate_vel.abs_y() < 0.08 or estimate_vel.y() * self.vel.y() < 0)):
                    
                    self.collision_estimated = True
            
            self.vel_count = self.face_count

            if sense_body.arm_expires() == 0:
                self.pointto_pos.invalidate()
                self.pointto_count = 1000
            
            if not self.collision_estimated:
                new_last_move=self.vel / self.player_type.player_decay()
                self.last_move.assign(new_last_move.x(), new_last_move.y())
            else:
                self.last_move.invalidate()
            
            if self.collision_estimated or self.collides_with_ball:
                self.last_moves[0].invalidate()
        
        self.attentionto_side = sense_body.attentionto_side()
        self.attentionto_unum = sense_body.attentionto_unum()
        self.tackle_expires = sense_body.tackle_expires()
        self.arm_movable = sense_body.arm_movable()
        self.arm_expires = sense_body.arm_expires()
        self.charge_expires = sense_body.charged_expires()
        self.card = sense_body.card()
        self.change_focus_count = sense_body.change_focus_count()
        self.focus_point_dist = sense_body.focus_point_dist()
        self.focus_point_dir = AngleDeg(sense_body.focus_point_dir())

    def set_pointto(self,point: Vector2D, done_time: GameTime):
        self.pointto_pos = point.copy()
        self.last_pointto_time = done_time
        
        if self.pos_valid():
            self.pointto_angle = (point - self.pos()).th()
            self.pointto_count = 0
    
    def update_ball_info(self, ball: BallObject):
        self.kickable = False
        self.kick_rate = 0
        self.catch_probability = 0
        self.tackle_probability = 0
        self.foul_probability = 0
        
        if self.pos_count > 100 or not ball.pos_valid():
            return
        
        self.dist_from_ball = ball.dist_from_self
        self.angle_from_ball = ball.angle_from_self + 180

        if ball.ghost_count > 0:
            return
        
        SP = ServerParam.i()
        ptype = self.player_type
        
        if SelfObject.DEBUG:
            log.os_log().debug(f"(self obj update ball_info) player_type_id={ptype.id()}")
            log.os_log().debug(f"(self obj update ball_info) kickable_area={ptype.kickable_area()}")

        if ball.dist_from_self <= ptype.kickable_area():
            buff = 0.055
            if ball.seen_pos_count >= 1:
                buff = 0.155
            if ball.seen_pos_count >= 2:
                buff = 0.255
            if ball.dist_from_self <= ptype.kickable_area() - buff:
                self.kickable = True
            
            self.kick_rate = ptype.kick_rate(ball.dist_from_self,
                                             (ball.angle_from_self - self.body).degree())

        if self.last_catch_time.cycle() + SP.catch_ban_cycle() <= self.time.cycle():
            self.catch_probability = ptype.get_catch_probability(self.pos, self.body, ball.pos, 0.055, 0.5)
        
        player2ball = (ball.pos - self.pos()).rotated_vector(-self.body)
        tackle_dist = SP.tackle_dist() if player2ball.x() > 0 else SP.tackle_back_dist()
        tackle_fail_prob = 1
        foul_fail_prob = 1
        
        if tackle_dist > 1e-5:
            tackle_fail_prob = ((player2ball.abs_x()/tackle_dist)**SP.tackle_exponent()
                                    + (player2ball.abs_y()/SP.tackle_width())**SP.tackle_exponent())
            foul_fail_prob = ((player2ball.abs_x()/tackle_dist)**SP.foul_exponent()
                                    + (player2ball.abs_y()/SP.tackle_width())**SP.foul_exponent())
            
        if tackle_fail_prob < 1:
            self.tackle_probability = 1 - tackle_fail_prob
        if foul_fail_prob < 1:
            self.foul_probability = 1 - foul_fail_prob
    
    def update_kickable_state(self,
                              ball: BallObject,
                              self_reach_cycle: int,
                              teammate_reach_cycle: int,
                              opponent_reach_cycle: int):
        if (not self.kickable
            and ball.seen_pos_count == 0
            and ball.dist_from_self < self.player_type.kickable_area() - 0.001):
            
            if (self_reach_cycle >= 10
                and opponent_reach_cycle < min(self_reach_cycle, teammate_reach_cycle) - 7):
                self.kickable = True
                return

            min_cycle = min(self_reach_cycle, teammate_reach_cycle, opponent_reach_cycle)
            ball_pos = ball.inertia_point(min_cycle)
            if ball_pos.abs_x() > ServerParam.i().pitch_half_length() or ball_pos.abs_y() > ServerParam.i().pitch_half_width():
                self.kickable = True
                return
            
        if opponent_reach_cycle > 0:
            self.foul_probability = 0
    
    def set_attentionto(self, side: SideID, unum: int):
        self.attentionto_side = side
        self.attentionto_unum = unum   
        
    def is_self(self):
        return True

    def focus_point(self) -> Vector2D:
        return self.pos + Vector2D.polar2vector(self.focus_point_dist, self.face + self.focus_point_dir)

    def str_sensed_body(self):
        return f'''
        self.sense_body_time
        
        '''

    def long_str(self):
        res = super(SelfObject, self).long_str()
        res += f'time: {self.time}, ' \
               f'sense_body_time: {self.sense_body_time}, ' \
               f'view_width: {self.view_width}, ' \
               f'neck: {self.neck}, ' \
               f'face_error: {self.face_error}, ' \
               f'stamina_model: {self.stamina_model}, ' \
               f'last_catch_time: {self.last_catch_time}, ' \
               f'tackle_expires: {self.tackle_expires}, ' \
               f'charge_expires: {self.charge_expires}, ' \
               f'arm_moveable: {self.arm_moveable}, ' \
               f'arm_expires: {self.arm_expires}, ' \
               f'pointto_rpos: {self.pointto_rpos}, ' \
               f'pointto_pos: {self.pointto_pos}, ' \
               f'last_pointto_time: {self.last_pointto_time}, ' \
               f'attentionto_side: {self.attentionto_side}, ' \
               f'attentionto_unum: {self.attentionto_unum}, ' \
               f'collision_estimated: {self.collision_estimated}, ' \
               f'collides_with_none: {self.collides_with_none}, ' \
               f'collides_with_ball: {self.collides_with_ball}, ' \
               f'collides_with_player: {self.collides_with_player}, ' \
               f'collides_with_post: {self.collides_with_post}, ' \
               f'kickable: {self.kickable}, ' \
               f'kick_rate: {self.kick_rate}, ' \
               f'catch_probability: {self.catch_probability}, ' \
               f'tackle_probability: {self.tackle_probability}, ' \
               f'foul_probability: {self.foul_probability}, ' \
               f'last_move: {self.last_move}, ' \
               f'last_moves: {self.last_moves}, ' \
               f'arm_movable: {self.arm_movable}, '
        return res

    def __str__(self):
        return f'''Self Player side:{self.side} unum:{self.unum} pos:{self.pos} vel:{self.vel} body:{self.body}'''

# TODO CHECK IT
'''        self.sense_body_time = current_time.copy()

        self.update_by_last_cycle(act, current_time)

        self.kicking = act.last_body_command() == CommandType.KICK or act.last_body_command() == CommandType.TACKLE
        self.view_width = sense_body.view_width()

        self.stamina_model.update_by_sense_body(sense_body.stamina(),
                                                 sense_body.effort(),
                                                 sense_body.stamina_capacity(),
                                                 current_time)

        if abs(self.neck.degree() - sense_body.neck_relative()) > 0.5:
            self.neck = AngleDeg(sense_body.neck_relative())

        if (sense_body.none_collided()
                or sense_body.ball_collided()
                or sense_body.player_collided()
                or sense_body.post_collided()):

            self.collision_estimated = False

            if sense_body.none_collided():
                self.collides_with_none = True
            if sense_body.ball_collided():
                self.collides_with_ball = True
                self.collision_estimated = True
            if sense_body.player_collided():
                self.collides_with_player = True
                self.collision_estimated = True
            if sense_body.post_collided():
                self.collides_with_post = True
                self.collision_estimated = True

        if self.face_valid():
            self.face = self.body + self.neck

            estimate_vel = self.vel.copy()
            sensed_speed_dir = sense_body.speed_dir()
            if sensed_speed_dir > 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir + 0.5)
            elif sensed_speed_dir < 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir - 0.5)

            vel_ang = self.face + sensed_speed_dir
            self.vel.set_polar(sense_body.speed_mag(), vel_ang)

            if (not self.has_sensed_collision()
                    and self.vel_valid()
                    and sense_body.speed_mag() < self.player_type().real_speed_max() * self.player_type().player_decay() * 0.11):

                if (estimate_vel.r() > 0.01
                        and sense_body.speed_mag() < estimate_vel.r() * 0.2
                        and (estimate_vel.abs_x() < 0.08 or estimate_vel.x() * self.vel.x() < 0)
                        and (estimate_vel.abs_y() < 0.08 or estimate_vel.y() * self.vel.y() < 0)):
                    self.collision_estimated = True

            self.vel_count = self.face_count()

            if sense_body.arm_expires() == 0:
                self.pointto_pos.invalidate()
                self.pointto_count = 1000

            if not self.collision_estimated:
                new_last_move = self.vel / self.player_type().player_decay()
                self.last_move.assign(new_last_move.x(), new_last_move.y())
            else:
                self.last_move.invalidate()

            if self.collision_estimated or self.collides_with_ball:
                self.last_moves[0].invalidate()

        self.attentionto_side = sense_body.attentionto_side()
        self.attentionto_unum = sense_body.attentionto_unum()
        self.tackle_expires = sense_body.tackle_expires()
        self.arm_movable = sense_body.arm_movable()
        self.arm_expires = sense_body.arm_expires()
        self.charge_expires = sense_body.charged_expires()
        self.card = sense_body.card()
        self.change_focus_count = sense_body.change_focus_count()
        self.focus_point_dist = sense_body.focus_point_dist()
        self.focus_point_dir = AngleDeg(sense_body.focus_point_dir())'''