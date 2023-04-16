from lib.debug.level import Level
from lib.player.localizer import Localizer
from lib.rcsc.game_time import GameTime
from lib.rcsc.player_type import PlayerType
from lib.player.object_ball import *
from lib.player.stamina_model import StaminaModel
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam as SP
from lib.rcsc.types import UNUM_UNKNOWN, SideID, Card, ViewWidth

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.localizer import Localizer
    from lib.player.world_model import WorldModel


class PlayerObject(Object):
    DEBUG = True
    
    def __init__(self, side: SideID = None, player: Localizer.PlayerT = None):
        super().__init__()
        self._unum: int = UNUM_UNKNOWN
        self._unum_count: int = 1000
        self._side: SideID = SideID.NEUTRAL
        self._goalie: bool = False
        self._player_type: PlayerType = PlayerType()
        self._player_type_id: Union[None, int] = None
        self._body: AngleDeg = AngleDeg(0)
        self._body_count: int = 1000
        self._face: AngleDeg = AngleDeg(0)
        self._face_count: int = 1000
        self._pointto_angle: float = 0
        self._pointto_count: int = 1000
        self._kick: bool = False
        self._tackle: bool = False
        self._charged: bool = False
        self._kicking: bool = False
        self._card: Card = Card.NO_CARD
        self._kick_rate: float = 0.0
        self._tackle_count: int = 1000

        if side is not None and player is not None:
            self._side = side
            self._unum = player.unum_
            self._goalie = player.goalie_
            self._pos = player.pos_.copy()
            self._pos_count = 0
            self._seen_pos = player.pos_.copy()
            self._seen_pos_count = 0

            if player.unum_ != UNUM_UNKNOWN:
                self._unum_count = 0

        self._pos_count_thr: Union[None, int] = 30
        self._relation_pos_count_thr: Union[None, int] = 30
        self._vel_count_thr: Union[None, int] = 5
        self._body_count_thr: Union[None, int] = 2

    # update with server data
    def init_dic(self, dic: dict):
        self._unum = int(dic["unum"])
        self._pos = Vector2D(float(dic["pos_x"]), float(dic["pos_y"]))
        self._vel = Vector2D(float(dic["vel_x"]), float(dic["vel_y"]))
        self._side = SideID.RIGHT if dic["side_id"] == 'r' else SideID.LEFT if dic["side_id"] == 'l' else SideID.NEUTRAL
        self._body = AngleDeg(float(dic["body"]))
        self._neck = AngleDeg(float(dic["neck"]))
        self._face = self._body + self._neck
        self._goalie = True if "goalie" in dic else False
        self._player_type_id = int(dic["player_type"])
        # self._pointto = Vector2D.invalid() TODO check this on full state
        # if "pointto_dist" in dic:
        #     self._pointto = Vector2D.polar2vector(float(dic["pointto_dist"]), float(dic["pointto_dir"]))
        self._stamina_model = StaminaModel(**dic["stamina"])
        self._kick = True if "kick" in dic else False
        self._tackle = True if "tackle" in dic else False
        self._charged = True if "charged" in dic else False
        self._card = Card.NO_CARD
        if "card" in dic:
            self._card = Card.YELLOW if dic["card"] == "y" else Card.RED
        self._kick_rate: float = 0.0
        self._rpos_count = 0
        self._vel_count = 0
        self._pos_count = 0
        self._body_count = 0
        self._ghost_count = 0

    def reverse_more(self):
        self._body.reverse()
        self._neck.reverse()  # TODO neck is relative?!?!?!

    def set_player_type(self, player_type: PlayerType):
        self._player_type = player_type
        self._player_type_id = player_type.id()

    def side(self):
        return self._side

    def body(self) -> AngleDeg:
        return self._body.copy()

    def neck(self):
        return self._neck

    def face(self):
        return self._face

    def goalie(self):
        return self._goalie

    def player_type(self) -> PlayerType:
        return self._player_type

    def pointto_angle(self):
        return self._pointto_angle

    def pointto_count(self):
        return self._pointto_count

    def stamina_model(self) -> StaminaModel:
        return self._stamina_model.copy()

    def stamina(self):
        return self._stamina_model.stamina()

    def recovery(self):
        return self._stamina_model.recovery()

    def kick(self):
        return self._kick

    def tackle(self):
        return self._tackle

    def charged(self):
        return self._charged

    def card(self):
        return self._card

    def set_kickable(self, ika: bool):
        self._kickable = ika

    def is_kickable(self, buf=0.05):
        if self.player_type() is None:
            return self.dist_from_ball() < ServerParam.i().kickable_area()
        return self.dist_from_ball() < self.player_type().kickable_area() - buf

    def kick_rate(self):
        return self._kick_rate

    def player_type_id(self):
        return self._player_type_id

    def inertia_point(self, n_step):
        return self.player_type().inertia_point(self.pos(), self.vel(), n_step)

    def inertia_final_point(self):
        return inertia_final_point(self.pos(),
                                   self.vel(),
                                   ServerParam.i().default_player_decay())

    def unum(self):
        return self._unum

    def effort(self):  # TODO update effort
        return SP.i().default_effort_max()

    def dash_rate(self):
        return self.effort() * self.player_type().dash_power_rate()

    def dist_from_ball(self):
        return self._dist_from_ball

    def tackle_probability(self):  # TODO should be written again
        return 0.25

    def is_tackling(self):
        return self._tackle 

    def tackle_count(self):
        return self._tackle_count

    def face_count(self):
        return self._face_count

    def is_frozen(self):
        return False 

    def is_ghost(self):
        return self._ghost_count > 0

    def body_count(self):
        return self._body_count

    def get_safety_dash_power(self, dash_power):
        return self.stamina_model().get_safety_dash_power(self.player_type(),
                                                          dash_power)
    
    def body_valid(self):
        return self._body_count < self._body_count_thr

    def update_by_last_cycle(self):
        self._pos_history = [self._pos] + self._pos_history
        if len(self._pos_history) > 100:
            self._pos_history = self._pos_history[:-1]
        
        if self.vel_valid():
            self._pos += self.vel()
        
        self._unum_count = min(1000, self._unum_count + 1)
        self._pos_count = min(1000, self._pos_count + 1)
        self._seen_pos_count = min(1000, self._seen_pos_count + 1)
        self._heard_pos_count = min(1000, self._heard_pos_count + 1)
        self._vel_count = min(1000, self._vel_count + 1)
        self._body_count = min(1000, self._body_count + 1)
        self._face_count = min(1000, self._face_count + 1)
        self._pointto_count = min(1000, self._pointto_count + 1)
        # self._kicking = min(1000, self._kicking + 1)
        self._tackle_count = min(1000, self._tackle_count + 1)
    
    def forgot(self):
        self._pos_count = 1000
        self._seen_pos_count = 1000
        self._heard_pos_count = 1000
        self._vel_count = 1000
        self._seen_vel_count = 1000
        self._face_count = 1000
        self._pointto_count = 1000
        self._tackle_count = 1000
    
    def update_by_see(self, side: SideID, player: Localizer.PlayerT):
        SP = ServerParam.i()

        self._side = side
        self._ghost_count = 0
        
        if player.unum_ != UNUM_UNKNOWN:
            self._unum = player.unum_
            self._unum_count = 0
            
            if not player.goalie_:
                self._goalie = False
        
        if player.goalie_:
            self._goalie = True
        
        last_seen_move = player.pos_ - self._seen_pos
        last_seen_pos_count = self._seen_pos_count
        
        if player.has_vel():
            self._vel = player.vel_
            self._vel_count = 0
            self._seen_vel = player.vel_
            self._seen_vel_count = 0
        elif (0 < self._pos_count <= 2
              and player.rpos_.r2() < 40**2):
            
            speed_max = self.player_type().real_speed_max() if self._player_type else SP.default_player_real_speed_max()
            decay = self.player_type().player_decay() if self.player_type() else SP.default_player_decay()
            self._vel = last_seen_move / last_seen_pos_count
            tmp = self._vel.r()

            if tmp > speed_max:
                self._vel *= speed_max / tmp
            
            self._vel *= decay
            self._vel_count = last_seen_pos_count
            self._seen_vel = self._vel.copy()
            self._seen_vel_count = 0
        else:
            self._vel = Vector2D(0, 0)
            self._vel_count = 1000
        
        self._pos = player.pos_.copy()
        self._seen_pos = player.pos_.copy()
        self._pos_count = 0
        self._seen_pos_count = 0
        
        if player.has_angle():
            self._body = AngleDeg(player.body_)
            self._face = AngleDeg(player.face_)
            self._body_count = 0
            self._face_count = 0
        elif last_seen_pos_count <= 2 and last_seen_move.r2() > 0.2**2:
            self._body = last_seen_move.th()
            self._body_count = max(0, last_seen_pos_count - 1)
            self._face = AngleDeg(0)
            self._face_count = 1000
        elif self.vel_valid() and self.vel().r2() > 0.2**2:
            self._body = self.vel().th()
            self._body_count = self.vel_count()
            self._face = AngleDeg(0)
            self._face_count = 1000
            
        if player.is_pointing() and self._pointto_count >= SP.point_to_ban():
            self._pointto_angle = player.arm_
            self._pointto_count = 0
        
        self._kicking = player.is_kicking()
        if player.is_tackling():
            if self._tackle_count > SP.tackle_cycles():
                self._tackle_count = 0
        elif player.rpos_.r2() > SP.visible_distance()**2:
            self._tackle_count = 1000
    
    def update_self_ball_related(self,
                                 self_pos: Vector2D,
                                 ball_pos: Vector2D):
        self._dist_from_self = (self.pos() - self_pos).r()
        self._angle_from_self = (self.pos() - self_pos).th()
        self._dist_from_ball = (self.pos() - ball_pos).r()
        self._angle_from_ball = (self.pos() - ball_pos).th()
    
    def set_team(self, side: SideID, unum: int, goalie: bool):
        self._side = side
        self._unum = unum
        self._goalie = goalie
    
    def update_by_hear(self, 
                       side: SideID,
                       unum: int,
                       goalie: bool,
                       pos: Vector2D,
                       body: float):
        
        if PlayerObject.DEBUG:
            log.sw_log().sensor().add_text( f"(update player by hear) unum={unum} prior_pos={self.pos()} new_pos={pos}")
        
        self._heard_pos = pos.copy()
        self._heard_pos_count = 0
        self._ghost_count = 0

        if side is not SideID.NEUTRAL:
            self._side = side
        
        if unum != UNUM_UNKNOWN and self._unum_count > 0:
            self._unum = unum
        
        self._goalie = goalie
        
        if self._unum_count > 2:
            self._unum_count = 2
            
        if (self._seen_pos_count >= 2
            or (self._seen_pos_count > 0 and self.dist_from_self() > 20)):
            self._pos = pos.copy()    
            self._pos_count = 1
        
        if body != -360:
            if self._body_count >= 2:
                self._body = AngleDeg(body)
                self._body_count = 1
    
    def is_self(self):
        return False
    
    def set_ghost(self):
        self._ghost_count += 1

    def is_goalie(self):
        return self._goalie

    def unum_count(self):
        return self._unum_count

    def long_str(self):
        res = f'unum: {self._unum} ' \
              f'side: {self._side} ' \
              f'body: {self._body} ' \
              f'goalie: {self._goalie} ' \
              f'player_type:({self._player_type}) ' \
              f'player_type_id: {self._player_type_id} ' \
              f'pointto_angle: {self._pointto_angle} ' \
              f'kick: {self._kick}' \
              f'tackle: {self._tackle}' \
              f'charged: {self._charged}' \
              f'kicking: {self._kicking}' \
              f'card: {self._card}' \
              f'kick_rate: {self._kick_rate}' \
              f'face: {self._face}' \
              f'body_count: {self._body_count}' \
              f'face_count: {self._face_count}' \
              f'pointto_count: {self._pointto_count}' \
              f'unum_count: {self._unum_count}' \
              f'tackle_count: {self._tackle_count}'
        res += super(PlayerObject, self).long_str()
        return res

    def __str__(self):
        return f'''Player side:{self._side.name} unum:{self._unum} pos:{self.pos()} vel:{self.vel()} body:{self._body} poscount:{self._pos_count} ghostcount:{self._ghost_count}'''

    def __repr__(self):
        return self.__str__()
