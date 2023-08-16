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
        self.unum: int = UNUM_UNKNOWN
        self.unum_count: int = 1000
        self.side: SideID = SideID.NEUTRAL
        self.goalie: bool = False
        self.player_type: PlayerType = PlayerType()
        self.player_type_id: Union[None, int] = None
        self.body: AngleDeg = AngleDeg(0)
        self.body_count: int = 1000
        self.face: AngleDeg = AngleDeg(0)
        self.face_count: int = 1000
        self.pointto_angle: float = 0
        self.pointto_count: int = 1000
        self.kick: bool = False
        self.tackle: bool = False
        self.charged: bool = False
        self.kicking: bool = False
        self.card: Card = Card.NO_CARD
        self.kick_rate: float = 0.0
        self.tackle_count: int = 1000

        if side is not None and player is not None:
            self.side = side
            self.unum = player.unum_
            self.goalie = player.goalie_
            self.pos = player.pos_.copy()
            self.pos_count = 0
            self.seen_pos = player.pos_.copy()
            self.seen_pos_count = 0

            if player.unum_ != UNUM_UNKNOWN:
                self.unum_count = 0

        self.pos_count_thr: Union[None, int] = 30
        self.relation_pos_count_thr: Union[None, int] = 30
        self.vel_count_thr: Union[None, int] = 5
        self.body_count_thr: Union[None, int] = 2

    # update with server data
    def init_dic(self, dic: dict):
        self.unum = int(dic["unum"])
        self.pos = Vector2D(float(dic["pos_x"]), float(dic["pos_y"]))
        self.vel = Vector2D(float(dic["vel_x"]), float(dic["vel_y"]))
        self.side = SideID.RIGHT if dic["side_id"] == 'r' else SideID.LEFT if dic["side_id"] == 'l' else SideID.NEUTRAL
        self.body = AngleDeg(float(dic["body"]))
        self.neck = AngleDeg(float(dic["neck"]))
        self.face = self.body + self.neck
        self.goalie = True if "goalie" in dic else False
        self.player_type_id = int(dic["player_type"])
        # self.pointto = Vector2D.invalid() TODO check this on full state
        # if "pointto_dist" in dic:
        #     self.pointto = Vector2D.polar2vector(float(dic["pointto_dist"]), float(dic["pointto_dir"]))
        self.stamina_model = StaminaModel(**dic["stamina"])
        self.kick = True if "kick" in dic else False
        self.tackle = True if "tackle" in dic else False
        self.charged = True if "charged" in dic else False
        self.card = Card.NO_CARD
        if "card" in dic:
            self.card = Card.YELLOW if dic["card"] == "y" else Card.RED
        self.kick_rate: float = 0.0
        self.rpos_count = 0
        self.vel_count = 0
        self.pos_count = 0
        self.body_count = 0
        self.ghost_count = 0

    def reverse_more(self):
        self.body.reverse()
        self.neck.reverse()  # TODO neck is relative?!?!?!

    def set_player_type(self, player_type: PlayerType):
        self.player_type = player_type
        self.player_type_id = player_type.id()

    def set_kickable(self, ika: bool):
        self.kickable = ika

    def is_kickable(self, buf=0.05):
        if self.player_type is None:
            return self.dist_from_ball < ServerParam.i().kickable_area()
        return self.dist_from_ball < self.player_type.kickable_area() - buf

    def inertia_point(self, n_step):
        return self.player_type.inertia_point(self.pos, self.vel, n_step)

    def inertia_final_point(self):
        return inertia_final_point(self.pos,
                                   self.vel,
                                   ServerParam.i().default_player_decay())

    def dash_rate(self):
        return self.stamina_model.effort() * self.player_type.dash_power_rate()

    def is_frozen(self):
        return False

    def is_ghost(self):
        return self.ghost_count > 0

    def get_safety_dash_power(self, dash_power):
        return self.stamina_model.get_safety_dash_power(self.player_type,
                                                          dash_power)
    
    def body_valid(self):
        return self.body_count < self.body_count_thr

    def update_by_last_cycle(self):
        self.pos_history = [self.pos] + self.pos_history
        if len(self.pos_history) > 100:
            self.pos_history = self.pos_history[:-1]
        
        if self.vel_valid():
            self.pos += self.vel
        
        self.unum_count = min(1000, self.unum_count + 1)
        self.pos_count = min(1000, self.pos_count + 1)
        self.seen_pos_count = min(1000, self.seen_pos_count + 1)
        self.heard_pos_count = min(1000, self.heard_pos_count + 1)
        self.vel_count = min(1000, self.vel_count + 1)
        self.body_count = min(1000, self.body_count + 1)
        self.face_count = min(1000, self.face_count + 1)
        self.pointto_count = min(1000, self.pointto_count + 1)
        # self.kicking = min(1000, self.kicking + 1)
        self.tackle_count = min(1000, self.tackle_count + 1)
    
    def forgot(self):
        self.pos_count = 1000
        self.seen_pos_count = 1000
        self.heard_pos_count = 1000
        self.vel_count = 1000
        self.seen_vel_count = 1000
        self.face_count = 1000
        self.pointto_count = 1000
        self.tackle_count = 1000
    
    def update_by_see(self, side: SideID, player: Localizer.PlayerT):
        SP = ServerParam.i()

        self.side = side
        self.ghost_count = 0
        
        if player.unum_ != UNUM_UNKNOWN:
            self.unum = player.unum_
            self.unum_count = 0
            
            if not player.goalie_:
                self.goalie = False
        
        if player.goalie_:
            self.goalie = True
        
        last_seen_move = player.pos_ - self.seen_pos
        last_seen_pos_count = self.seen_pos_count
        
        if player.has_vel():
            self.vel = player.vel_
            self.vel_count = 0
            self.seen_vel = player.vel_
            self.seen_vel_count = 0
        elif (0 < self.pos_count <= 2
              and player.rpos_.r2() < 40**2):
            
            speed_max = self.player_type.real_speed_max() if self.player_type else SP.default_player_real_speed_max()
            decay = self.player_type.player_decay() if self.player_type else SP.default_player_decay()
            self.vel = last_seen_move / last_seen_pos_count
            tmp = self.vel.r()

            if tmp > speed_max:
                self.vel *= speed_max / tmp
            
            self.vel *= decay
            self.vel_count = last_seen_pos_count
            self.seen_vel = self.vel.copy()
            self.seen_vel_count = 0
        else:
            self.vel = Vector2D(0, 0)
            self.vel_count = 1000
        
        self.pos = player.pos_.copy()
        self.seen_pos = player.pos_.copy()
        self.pos_count = 0
        self.seen_pos_count = 0
        
        if player.has_angle():
            self.body = AngleDeg(player.body_)
            self.face = AngleDeg(player.face_)
            self.body_count = 0
            self.face_count = 0
        elif last_seen_pos_count <= 2 and last_seen_move.r2() > 0.2**2:
            self.body = last_seen_move.th()
            self.body_count = max(0, last_seen_pos_count - 1)
            self.face = AngleDeg(0)
            self.face_count = 1000
        elif self.vel_valid() and self.vel.r2() > 0.2**2:
            self.body = self.vel.th()
            self.body_count = self.vel_count
            self.face = AngleDeg(0)
            self.face_count = 1000
            
        if player.is_pointing() and self.pointto_count >= SP.point_to_ban():
            self.pointto_angle = player.arm_
            self.pointto_count = 0
        
        self.kicking = player.is_kicking()
        if player.is_tackling():
            if self.tackle_count > SP.tackle_cycles():
                self.tackle_count = 0
        elif player.rpos_.r2() > SP.visible_distance()**2:
            self.tackle_count = 1000
    
    def update_self_ball_related(self,
                                 self_pos: Vector2D,
                                 ball_pos: Vector2D):
        self.dist_from_self = (self.pos - self_pos).r()
        self.angle_from_self = (self.pos - self_pos).th()
        self.dist_from_ball = (self.pos - ball_pos).r()
        self.angle_from_ball = (self.pos - ball_pos).th()
    
    def set_team(self, side: SideID, unum: int, goalie: bool):
        self.side = side
        self.unum = unum
        self.goalie = goalie
    
    def update_by_hear(self, 
                       side: SideID,
                       unum: int,
                       goalie: bool,
                       pos: Vector2D,
                       body: float):
        
        if PlayerObject.DEBUG:
            log.sw_log().sensor().add_text( f"(update player by hear) unum={unum} prior_pos={self.pos} new_pos={pos}")
        
        self.heard_pos = pos.copy()
        self.heard_pos_count = 0
        self.ghost_count = 0

        if side is not SideID.NEUTRAL:
            self.side = side
        
        if unum != UNUM_UNKNOWN and self.unum_count > 0:
            self.unum = unum
        
        self.goalie = goalie
        
        if self.unum_count > 2:
            self.unum_count = 2
            
        if (self.seen_pos_count >= 2
            or (self.seen_pos_count > 0 and self.dist_from_self > 20)):
            self.pos = pos.copy()
            self.pos_count = 1
        
        if body != -360:
            if self.body_count >= 2:
                self.body = AngleDeg(body)
                self.body_count = 1
    
    def is_self(self):
        return False
    
    def set_ghost(self):
        self.ghost_count += 1

    def is_goalie(self):
        return self.goalie

    def long_str(self):
        res = f'unum: {self.unum} ' \
              f'side: {self.side} ' \
              f'body: {self.body} ' \
              f'goalie: {self.goalie} ' \
              f'player_type:({self.player_type}) ' \
              f'player_type_id: {self.player_type_id} ' \
              f'pointto_angle: {self.pointto_angle} ' \
              f'kick: {self.kick}' \
              f'tackle: {self.tackle}' \
              f'charged: {self.charged}' \
              f'kicking: {self.kicking}' \
              f'card: {self.card}' \
              f'kick_rate: {self.kick_rate}' \
              f'face: {self.face}' \
              f'body_count: {self.body_count}' \
              f'face_count: {self.face_count}' \
              f'pointto_count: {self.pointto_count}' \
              f'unum_count: {self.unum_count}' \
              f'tackle_count: {self.tackle_count}'
        res += super(PlayerObject, self).long_str()
        return res

    def __str__(self):
        return f'''Player side:{self.side.name} unum:{self.unum} pos:{self.pos} vel:{self.vel} body:{self.body} poscount:{self.pos_count} ghostcount:{self.ghost_count}'''

    def __repr__(self):
        return self.__str__()
