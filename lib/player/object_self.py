from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.soccer_math import min_max
from pyrusgeom.vector_2d import Vector2D
from lib.player.action_effector import ActionEffector
from lib.player.object_ball import BallObject
from lib.player.object_player import PlayerObject
from lib.player.sensor.body_sensor import BodySensor
from lib.player.stamina_model import StaminaModel
from lib.player_command.player_command import CommandType
from lib.rcsc.game_time import GameTime
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import SideID, ViewQuality, ViewWidth
from lib.debug.debug_print import debug_print


class SelfObject(PlayerObject):
    FACE_COUNT_THR = 5
    DEBUG = True
    
    def __init__(self, player: PlayerObject = None):
        super().__init__()

        self._time: GameTime = GameTime()
        self._sense_body_time: GameTime = GameTime()

        self._view_width: ViewWidth = ViewWidth.ILLEGAL
        self._view_quality: ViewQuality = ViewQuality.ILLEGAL

        self._neck: AngleDeg = AngleDeg(0)

        self._stamina_model: StaminaModel = StaminaModel()

        self._last_catch_time: GameTime = GameTime()

        self._tackle_expires: int = 0
        self._charge_expires: int = 0

        self._arm_moveable: int = 0
        self._arm_expires: int = 0

        self._pointto_rpos: Vector2D = Vector2D.invalid()
        self._pointto_pos: Vector2D = Vector2D.invalid()
        self._last_pointto_time: GameTime = GameTime()

        self._attentionto_side: SideID = SideID.NEUTRAL
        self._attentionto_unum: int = 0

        self._collision_estimated: bool = False
        self._collides_with_none: bool = False
        self._collides_with_ball: bool = False
        self._collides_with_player: bool = False
        self._collides_with_post: bool = False

        self._kickable: bool = False
        self._kick_rate: float = 0
        self._catch_probability: float = 0
        self._tackle_probability: float = 0
        self._foul_probability: float = 0
                
        self._last_move: Vector2D = Vector2D(0,0)
        self._last_moves: list[Vector2D] = [Vector2D(0,0) for _ in range(4)]
        
        self._arm_movable: int = 0
        if player:
            self._unum = player._unum
            self._pos = player._pos
            self._vel = player._vel
            self._side = player._side
            self._body = player._body
            self._neck = player._neck
            self._goalie = player._goalie
            self._player_type_id = player._player_type_id
            self._stamina_model = player._stamina_model
            self._kick = player._kick
            self._tackle = player._tackle
            self._charged = player._charged
            self._card = player._card
            self._card = player._card
            self._kick_rate = player._kick_rate
            self._rpos_count = 0
            self._vel_count = 0
            self._pos_count = 0
            self._body_count = 0
            self._change_focus_count = 0
            self._focus_point_dist = 0
            self._focus_point_dir_to_neck = AngleDeg(0)
            self._focus_point_dir_to_body = AngleDeg(0)
            self._focus_point_dir_to_pos = AngleDeg(0)
            self._focus_point = player.pos()
    
    def init(self, side: SideID, unum: int, goalie: bool):
        self._side = side
        self._unum = unum
        self._goalie = goalie

    def view_width(self):
        return self._view_width

    def view_quality(self):
        return self._view_quality
    
    def face(self):
        return self._face
    
    def is_frozen(self):
        return self._tackle_expires > 0 or self._charge_expires > 0
    
    def face_valid(self):
        return self._face_count < SelfObject.FACE_COUNT_THR
    
    def last_move(self, index=None):
        if index:
            index = min_max(0, index, len(self._last_moves)-1)
            return self._last_moves[index] 
        return self._last_move
    
    def is_kicking(self):
        return self._kicking
    
    def is_kickable(self):
        return self._kickable
    
    def set_view_mode(self, vw: ViewWidth, vq:ViewQuality):
        self._view_width = vw
        self._view_quality = vq

    def catch_time(self):
        return self._last_catch_time
    
    def update(self, act: ActionEffector, current_time: GameTime):
        if self._time == current_time:
            return
        
        SP = ServerParam.i()
        
        self._time = current_time.copy()
        self._kicking = False
        
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
                self._tackle_expires = SP.tackle_cycles()
            self._kicking = True

        elif act.last_body_command() == CommandType.MOVE:
            self._pos = act.get_move_pos()

        elif act.last_body_command() == CommandType.CATCH:
            pass
        
        elif act.last_body_command() == CommandType.KICK:
            self._kicking = True
        
        if act.done_turn_neck():
            neck_moment = act.get_turn_neck_moment()
        self._neck += min_max(SP.min_neck_angle(), neck_moment, SP.max_neck_angle())

        self._stamina_model.simulate_dash(self.player_type(), dash_power)
        
        self._body += turn_moment
        self._face = self._body + self._neck
        
        if self.vel_valid():
            self._vel += accel
        if self.pos_valid():
            self._pos += self._vel
        self._vel *= self.player_type().player_decay()
        
        self._pos_count += 1
        self._seen_pos_count += 1
        self._vel_count += 1
        self._seen_vel_count += 1
        self._body_count += 1
        self._face_count += 1
        self._pointto_count = min(1000, self._pointto_count + 1)
        
        self._tackle_expires = max(0, self._tackle_expires - 1)
        self._charge_expires = max(0, self._charge_expires - 1)
        self._arm_movable = max(0, self._arm_movable - 1)
        self._arm_expires = max(0, self._arm_expires - 1)
        
        self._last_move = self._vel / self.player_type().player_decay()
        self._last_moves = [self._last_move] + self._last_moves[0:-1]

        self._collision_estimated = False
        self._collides_with_none = False
        self._collides_with_ball = False
        self._collides_with_player = False
        self._collides_with_post = False

    def update_angle_by_see(self, face: float, current_time: GameTime):
        self._time = current_time.copy()
        self._face = AngleDeg(face)
        self._body = AngleDeg(face - self._neck.degree())
        self._focus_point_dir_to_pos = self.face() - self.focus_point_dir_to_neck()
        self._focus_point_dir_to_body = self.focus_point_dir_to_pos() - self.body()

        self._body_count = 0
        self._face_count = 0
        
    def update_vel_dir_after_see(self, sense: BodySensor, current_time: GameTime):
        if sense.time() != current_time:
            debug_print("(update vel dir after see) sense time does not match current time")
            return
        
        if self.face_count() == 0:
            sensed_speed_dir = sense.speed_dir()
            if sensed_speed_dir > 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir + 0.5)
            elif sensed_speed_dir < 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir - 0.5)

            vel_ang = self._face + sensed_speed_dir
            
            self._vel.set_polar(sense.speed_mag(), vel_ang)
            self._vel_count = 0
            self._seen_vel = self.vel().copy()
            self._seen_vel_count = 0
            
            if not self._collision_estimated:
                new_last_move = self._vel/self.player_type().player_decay()
                self._last_move.assign(new_last_move.x(), new_last_move.y())
    
    def update_pos_by_see(self, pos: Vector2D, face: float, current_time: GameTime):
        self._time = current_time.copy()
        
        if (self._pos_count == 1
            and self._seen_pos_count == 1
            and (self._collision_estimated
                 or not self._last_move.is_valid())):
            new_last_move = self._pos - self._seen_pos
            self._last_move.assign(new_last_move.x(), new_last_move.y())

        self._pos = pos.copy()
        self._seen_pos = pos.copy()
        self._face = AngleDeg(face)
        self._body = AngleDeg(face) - self._neck

        self._focus_point_dir_to_pos = self.face() - self.focus_point_dir_to_neck()
        self._focus_point_dir_to_body = self.focus_point_dir_to_pos() - self.body()
        self._focus_point = self._pos + Vector2D.polar2vector(self.focus_point_dist(), self.focus_point_dir_to_pos())

        self._pos_count = 0
        self._seen_pos_count = 0
        self._body_count = 0
        self._face_count = 0
    
    def has_sensed_collision(self):
        return(
            self._collides_with_none
            or self._collides_with_ball
            or self._collides_with_player
            or self._collides_with_post
        )
    
    def update_after_sense_body(self, body: BodySensor, act:ActionEffector, current_time:GameTime):
        if self._sense_body_time == current_time:
            debug_print(f"(self update after see) called twice at {current_time}")
            return
        
        self._sense_body_time = current_time.copy()

        self.update(act, current_time)

        self._kicking = act.last_body_command() == CommandType.KICK or act.last_body_command() == CommandType.TACKLE
        self._view_width = body.view_width()
        self._view_quality = body.view_quality()
        
        self._stamina_model.update_by_sense_body(body.stamina(),
                                                 body.effort(),
                                                 body.stamina_capacity(),
                                                 current_time)
        
        if abs(self._neck.degree() - body.neck_relative()) > 0.5:
            self._neck = AngleDeg(body.neck_relative())
        
        if (body.none_collided() 
            or body.ball_collided()
            or body.player_collided()
            or body.post_collided()):
            
            self._collision_estimated = False
            
            if body.none_collided():
                self._collides_with_none = True
            if body.ball_collided():
                self._collides_with_ball = True
                self._collision_estimated = True
            if body.player_collided():
                self._collides_with_player = True
                self._collision_estimated = True
            if body.post_collided():
                self._collides_with_post = True
                self._collision_estimated = True

        if self.face_valid():
            self._face = self._body + self._neck
            
            estimate_vel = self._vel.copy()
            sensed_speed_dir = body.speed_dir()
            if sensed_speed_dir > 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir + 0.5)
            elif sensed_speed_dir < 0:
                sensed_speed_dir = AngleDeg.normalize_angle(sensed_speed_dir - 0.5)
            
            vel_ang = self._face + sensed_speed_dir
            self._vel.set_polar(body.speed_mag(), vel_ang)

            if (not self.has_sensed_collision()
                and self.vel_valid()
                and body.speed_mag() < self.player_type().real_speed_max()*self.player_type().player_decay()*0.11):
                
                if (estimate_vel.r() > 0.01
                    and body.speed_mag() < estimate_vel.r() *0.2
                    and (estimate_vel.abs_x() < 0.08 or estimate_vel.x() * self._vel.x() < 0)
                    and (estimate_vel.abs_y() < 0.08 or estimate_vel.y() * self._vel.y() < 0)):
                    
                    self._collision_estimated = True
            
            self._vel_count = self.face_count()

            if body.arm_expires() == 0:
                self._pointto_pos.invalidate()
                self._pointto_count = 1000
            
            if not self._collision_estimated:
                new_last_move=self._vel / self.player_type().player_decay()
                self._last_move.assign(new_last_move.x(), new_last_move.y())
            else:
                self._last_move.invalidate()
            
            if self._collision_estimated or self._collides_with_ball:
                self._last_moves[0].invalidate()
        
        self._attentionto_side = body.attentionto_side()
        self._attentionto_unum = body.attentionto_unum()
        self._tackle_expires = body.tackle_expires()
        self._arm_movable = body.arm_movable()
        self._arm_expires = body.arm_expires()
        self._charge_expires = body.charged_expires()
        self._card = body.card()
        self._change_focus_count = body.change_focus_count()
        self._focus_point_dist = body.focus_point_dist()
        self._focus_point_dir_to_neck = body.focus_point_dir()

    def set_pointto(self,point: Vector2D, done_time: GameTime):
        self._pointto_pos = point.copy()
        self._last_pointto_time = done_time
        
        if self.pos_valid():
            self._pointto_angle = (point - self.pos()).th()
            self._pointto_count = 0
    
    def update_ball_info(self, ball: BallObject):
        self._kickable = False
        self._kick_rate = 0
        self._catch_probability = 0
        self._tackle_probability = 0
        self._foul_probability = 0
        
        if self.pos_count() > 100 or not ball.pos_valid():
            return
        
        self._dist_from_ball = ball.dist_from_self()
        self._angle_from_ball = ball.angle_from_self() + 180

        if ball.ghost_count() > 0:
            return
        
        SP = ServerParam.i()
        ptype = self.player_type()
        
        if SelfObject.DEBUG:
            debug_print(f"(self obj update ball_info) player_type_id={ptype.id()}")
            debug_print(f"(self obj update ball_info) kickable_area={ptype.kickable_area()}")

        if ball.dist_from_self() <= ptype.kickable_area():
            buff = 0.055
            if ball.seen_pos_count() >= 1:
                buff = 0.155
            if ball.seen_pos_count() >= 2:
                buff = 0.255
            if ball.dist_from_self() <= ptype.kickable_area() - buff:
                self._kickable = True
            
            self._kick_rate = ptype.kick_rate(ball.dist_from_self(),
                                             (ball.angle_from_self() - self.body()).degree())

        if self._last_catch_time.cycle() + SP.catch_ban_cycle() <= self._time.cycle():
            self._catch_probability = ptype.get_catch_probability(self.pos(), self.body(), ball.pos(), 0.055, 0.5)
        
        player2ball = (ball.pos() - self.pos()).rotated_vector(-self.body())
        tackle_dist = SP.tackle_dist() if player2ball.x() > 0 else SP.tackle_back_dist()
        tackle_fail_prob = 1
        foul_fail_prob = 1
        
        if tackle_dist > 1e-5:
            tackle_fail_prob = ((player2ball.abs_x()/tackle_dist)**SP.tackle_exponent()
                                    + (player2ball.abs_y()/SP.tackle_width())**SP.tackle_exponent())
            foul_fail_prob = ((player2ball.abs_x()/tackle_dist)**SP.foul_exponent()
                                    + (player2ball.abs_y()/SP.tackle_width())**SP.foul_exponent())
            
        if tackle_fail_prob < 1:
            self._tackle_probability = 1 - tackle_fail_prob
        if foul_fail_prob < 1:
            self._foul_probability = 1 - foul_fail_prob
    
    def update_kickable_state(self,
                              ball: BallObject,
                              self_reach_cycle: int,
                              teammate_reach_cycle: int,
                              opponent_reach_cycle: int):
        if (not self._kickable
            and ball.seen_pos_count() == 0
            and ball.dist_from_self() < self.player_type().kickable_area() - 0.001):
            
            if (self_reach_cycle >= 10
                and opponent_reach_cycle < min(self_reach_cycle, teammate_reach_cycle) - 7):
                debug_print("KA A")
                self._kickable = True
                return

            min_cycle = min(self_reach_cycle, teammate_reach_cycle, opponent_reach_cycle)
            ball_pos = ball.inertia_point(min_cycle)
            if ball_pos.abs_x() > ServerParam.i().pitch_half_length() or ball_pos.abs_y() > ServerParam.i().pitch_half_width():
                debug_print("KA B")
                self._kickable = True
                return
            
        if opponent_reach_cycle > 0:
            self._foul_probability = 0
    
    def attentionto_side(self):
        return self._attentionto_side
        
    def attentionto_unum(self):
        return self._attentionto_unum
    
    def set_attentionto(self, side: SideID, unum: int):
        self._attentionto_side = side
        self._attentionto_unum = unum   
        
    def is_self(self):
        return False

    def tackle_probability(self):
        return self._tackle_probability

    def foul_probability(self):
        return self._foul_probability

    def change_focus_count(self):
        return self._change_focus_count

    def focus_point_dist(self):
        return self._focus_point_dist

    def focus_point_dir_to_neck(self):
        return self._focus_point_dir_to_neck

    def focus_point_dir_to_body(self):
        return self._focus_point_dir_to_body

    def focus_point_dir_to_pos(self):
        return self._focus_point_dir_to_pos

