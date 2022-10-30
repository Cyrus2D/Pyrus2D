from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.player.action_effector import ActionEffector
from lib.player.localizer import Localizer
from lib.rcsc.game_time import GameTime
from lib.rcsc.player_type import PlayerType
from lib.player.object_ball import *
from lib.player.stamina_model import StaminaModel
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam as SP
from lib.rcsc.types import UNUM_UNKNOWN, SideID, Card, ViewQuality, ViewWidth


# from lib.player.templates import *


class PlayerObject(Object):
    POS_COUNT_THR = 30
    VEL_COUNT_THR = 5
    
    def __init__(self, side: SideID = None, player = None):
        super().__init__()
        self._unum: int = 0
        self._side: SideID = SideID.NEUTRAL
        self._body: AngleDeg = AngleDeg(0)
        self._goalie: bool = False
        self._player_type: PlayerType = None
        self._player_type_id: int = None
        self._pointto_angle: float = 0
        self._kick: bool = False
        self._tackle: bool = False
        self._charged: bool = False
        self._card: Card = Card.NO_CARD
        self._kickable: bool = False  # TODO does it change?
        self._kickrate: float = 0.0
        self._dist_from_ball: float = 0.0
        self._angle_from_ball: AngleDeg = AngleDeg(0.0)
        self._face: float = 0
        
        self._pos_history: list[Vector2D] = []

        self._body_count: int = 1000
        self._face_count:int = 1000
        self._pointto_count: int = 1000
        self._kicking = False

        self._tackle_count: int = 1000
        
        if side is not None and player is not None:
            self._side = side
            self._unum = player._unum
            self._goalie = player._goalie
            self._pos = player._pos
            self._pos_count = 0
            self._seen_pos = player._seen_pos
            self._seen_pos_count = 0
            
            if player._unum != UNUM_UNKNOWN:
                self._unum_count = 0
            


    # update with server data
    def init_dic(self, dic: dict):
        self._unum = int(dic["unum"])
        self._pos = Vector2D(float(dic["pos_x"]), float(dic["pos_y"]))
        self._vel = Vector2D(float(dic["vel_x"]), float(dic["vel_y"]))
        self._side = SideID.RIGHT if dic["side_id"] == 'r' else SideID.LEFT if dic["side_id"] == 'l' else SideID.NEUTRAL
        self._body = AngleDeg(float(dic["body"]))
        self._neck = AngleDeg(float(dic["neck"]))
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
        self._kickable: bool = False
        self._kickrate: float = 0.0
        self._dist_from_ball: float = 0.0
        self._angle_from_ball: float = 0.0

    # update other data
    def _update_more_with_full_state(self, wm):
        ball = wm.ball()
        self._kickable = False
        self._kickrate = 0.0

        self._dist_from_ball = ball.pos().dist(self._pos)
        self._angle_from_ball = (self._pos - wm.ball().pos()).th() + AngleDeg(180.0)

        dlog.add_text(Level.KICK, f"_dist_from_ball={self._dist_from_ball}")
        # -----------------------------------------------------
        # check kickable

        if self._dist_from_ball <= self._player_type.kickable_area():
            buf = 0.055
            if self._dist_from_ball <= self.player_type().kickable_area() - buf:
                self._kickable = True

            self._kickrate = kick_rate(self._dist_from_ball,
                                       (self._angle_from_ball - self._body).degree(),
                                       self.player_type().kick_power_rate(),
                                       SP.i().ball_size(),
                                       self.player_type().player_size(),
                                       self.player_type().kickable_margin())
        dlog.add_text(Level.KICK, f"_kickable={self._kickable}")

        # relative pos

        #
        # # kickable
        # if self.player_type() is not None:  # TODO its wrong
        #     if self.pos().dist(wm.ball().pos()) < self.player_type().kickable_area():
        #         self._kickable = True
        #     else:
        #         self._kickable = False
        #
        # # dist from ball
        # self._dist_from_ball = self.pos().dist(wm.ball().pos())

        # def update_ball_info(self, wm):

    def reverse_more(self):
        self._body.reverse()
        self._neck.reverse()  # TODO neck is relative?!?!?!

    def __repr__(self):
        return "(side: " + str(self.side().name) + ")(unum: " + str(self._unum) + ")(pos: " + str(
            self.pos()) + ")(vel: " + str(self.vel()) + ")"

    def set_player_type(self, player_type: PlayerType):
        self._player_type = player_type

    def side(self):
        return self._side

    def body(self) -> AngleDeg:
        return self._body.copy()

    def neck(self):
        return self._neck

    def goalie(self):
        return self._goalie

    def player_type(self)-> PlayerType:
        return self._player_type

    def pointto_angle(self):
        return self._pointto_angle

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

    def is_kickable(self):
        return self._kickable

    def kick_rate(self):
        return self._kickrate

    def player_type_id(self):
        return self._player_type_id

    def inertia_point(self, n_step):
        return self.player_type().inertia_point(self.pos(), self.vel(), n_step)

    def inertia_final_point(self):
        return inertia_final_point(self.pos(),
                                   self.vel(),
                                   ServerParam.i().player_decay())

    def unum(self):
        return self._unum

    def effort(self):  # TODO update effort
        return SP.i().effort_init()

    def dash_rate(self):
        return self.effort() * self.player_type().dash_power_rate()

    def dist_from_ball(self):
        return self._dist_from_ball

    def tackle_probability(self):  # TODO should be written again
        return 0.25

    def is_tackling(self):
        return False  # TODO 

    def tackle_count(self):
        return 0  # TODO 

    def face_count(self):
        return 0

    def is_frozen(self):
        return False  # TODO 

    def is_ghost(self):
        return False  # TODO should 

    def body_count(self):
        return self._body_count

    def set_view_mode(self, vw: ViewWidth, vq:ViewQuality):
        self._view_width = vw.copy()
        self._view_quality = vq.copy()

    def get_safety_dash_power(self, dash_power):
        return self.stamina_model().get_safety_dash_power(self.player_type(),
                                                          dash_power)
    
    def vel_valid(self):
        return self.vel_count() < PlayerObject.VEL_COUNT_THR

    def pos_valid(self):
        return self.pos_count() < PlayerObject.POS_COUNT_THR

    def update(self):
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
        self._kicking = min(1000, self._kicking + 1)
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
            
            speed_max = self.player_type().real_speed_max() if self._player_type else SP.defaulreal()
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
            self._body = player.body_
            self._face = player.face_
            self._body_count = 0
            self._face_count = 0
        elif last_seen_pos_count <= 2 and last_seen_move.r2() > 0.2**2:
            self._body = last_seen_move.th()
            self._body_count = max(0, last_seen_pos_count - 1)
            self._face = 0
            self._face_count = 1000
        elif self.vel_valid() and self.vel().r2() > 0.2**2:
            self._body = self.vel().th()
            self._body_count = self.vel_count()
            self._face = 0
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
            
        