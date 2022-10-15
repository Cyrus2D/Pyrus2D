from lib.math.angle_deg import AngleDeg
from lib.math.soccer_math import min_max
from lib.math.vector_2d import Vector2D
from lib.player.action_effector import ActionEffector
from lib.player.object_player import PlayerObject
from lib.player.stamina_model import StaminaModel
from lib.player_command.player_command import CommandType
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import SideID, ViewQuality, ViewWidth


class SelfObject(PlayerObject):
    def __init__(self):
        super().__init__()
        self._time: GameTime = GameTime()

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
        self._Attentionto_unum: int = 0

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

    def view_width(self):
        return self._view_width

    def view_quality(self):
        return self._view_quality
    
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

        self._collision_estimated = False
        self._collides_with_none = False
        self._collides_with_ball = False
        self._collides_with_player = False
        self._collides_with_post = False

