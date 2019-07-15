from lib.player.object import *
from lib.rcsc.player_type import PlayerType
from lib.player.stamina import Stamina
from lib.rcsc.types import SideID, Card


class PlayerObject(Object):
    def __init__(self):
        super().__init__()
        self._unum: int = 0
        self._side: SideID = SideID.NEUTRAL
        self._body: AngleDeg = AngleDeg(0)
        self._neck: AngleDeg = AngleDeg(0)
        self._goalie: bool = False
        self._player_type: PlayerType = None
        self._player_type_id: int = None
        self._pointto: Vector2D = Vector2D.invalid()
        self._stamina: Stamina = Stamina()
        self._kick: bool = False
        self._tackle: bool = False
        self._charged: bool = False
        self._card: Card = Card.NO_CARD

    def init_dic(self, dic: dict):
        self._unum = int(dic["unum"])
        self._pos = Vector2D(float(dic["pos_x"]), float(dic["pos_y"]))
        self._vel = Vector2D(float(dic["vel_x"]), float(dic["vel_y"]))
        self._side = SideID.RIGHT if dic["side_id"] == 'r' else SideID.LEFT if dic["side_id"] == 'l' else SideID.NEUTRAL
        self._body = AngleDeg(float(dic["body"]))
        self._neck = AngleDeg(float(dic["neck"]))
        self._goalie = True if "goalie" in dic else False
        self._player_type_id = int(dic["player_type"])
        self._pointto = Vector2D.invalid()
        if "pointto_dist" in dic:
            self._pointto = Vector2D.polar2vector(dic["pointto_dist"], dic["pointto_dir"])
        self._stamina = Stamina(**dic["stamina"])
        self._kick = True if "kick" in dic else False
        self._tackle = True if "tackle" in dic else False
        self._charged = True if "charged" in dic else False
        self._card = Card.NO_CARD
        if "card" in dic:
            self._card = Card.YELLOW if dic["card"] == "y" else Card.RED

    def __repr__(self):
        return "(side: " + str(self.side().name) + ")(unum: " + str(self.unum()) + ")(pos: " + str(
            self.pos()) + ")(vel: " + str(self.vel()) + ")"

    def set_player_type(self, player_type: PlayerType):
        self._player_type = player_type

    def unum(self):
        return self._unum

    def side(self):
        return self._side

    def body(self):
        return self._body

    def neck(self):
        return self._neck

    def goalie(self):
        return self._goalie

    def player_type(self):
        return self._player_type

    def pointto(self):
        return self._pointto

    def stamina(self):
        return self._stamina

    def kick(self):
        return self._kick

    def tackle(self):
        return self._tackle

    def charged(self):
        return self._charged

    def card(self):
        return self._card

    def player_type_id(self):
        return self._player_type_id
