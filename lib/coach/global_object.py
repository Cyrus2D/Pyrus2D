from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.vector_2d import Vector2D
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import SideID, Card


class GlobalBallObject:
    def __init__(self):
        self._pos: Vector2D = Vector2D(0, 0)
        self._vel: Vector2D = Vector2D(0, 0)

    def init_str(self, string: str):
        data = string.split(" ")
        self._pos = Vector2D(float(data[0]), float(data[1]))
        self._vel = Vector2D(float(data[2]), float(data[3]))


    def pos(self) -> Vector2D:
        return self._pos

    def vel(self) -> Vector2D:
        return self._vel

    def set_pos(self, x, y):
        self._pos.assign(x, y)

    def set_vel(self, x, y):
        self._vel.assign(x, y)

    def reverse(self):
        self._pos.reverse()
        self._vel.reverse()


class GlobalPlayerObject:
    def __init__(self):
        self._side: SideID = SideID.NEUTRAL
        self._unum: int = -1
        self._goalie: bool = False
        self._type = -1
        self._player_type: PlayerType = PlayerType()
        self._pos: Vector2D = Vector2D.invalid()
        self._vel: Vector2D = Vector2D(0, 0)
        self._body: AngleDeg = AngleDeg(0)
        self._face: AngleDeg = AngleDeg(0)
        self._recovery: float = ServerParam.i().recover_init()
        self._pointto_cycle: int = 0
        self._pointto_angle: AngleDeg = AngleDeg(0)
        self._kicked: bool = False
        self._tackle_cycle: int = 0
        self._charged_cycle: int = 0
        self._card: Card = Card.NO_CARD

    def init_dic(self, dic: dict):
        self._unum = int(dic["unum"])
        self._pos = Vector2D(float(dic["pos_x"]), float(dic["pos_y"]))
        self._vel = Vector2D(float(dic["vel_x"]), float(dic["vel_y"]))
        self._side = SideID.RIGHT if dic["side_id"] == 'r' else SideID.LEFT if dic["side_id"] == 'l' else SideID.NEUTRAL
        self._body = AngleDeg(float(dic["body"]))
        self._face = AngleDeg(float(dic["neck"]))
        self._goalie = True if "goalie" in dic else False
        self._point_to = Vector2D.invalid()
        if "pointto_dist" in dic:
            self._point_to = Vector2D.polar2vector(float(dic["pointto_dist"]), float(dic["pointto_dir"]))
        self._kicked = True if "kick" in dic else False
        if "tackle" in dic:
             self._tackle_cycle = 1
        if "charged" in dic:
            self._charged_cycle = 1
        if "card" in dic:
            self._card = Card.YELLOW if dic["card"] == "y" else Card.RED

    def side(self) -> SideID:
        return self._side

    def unum(self) -> int:
        return self._unum

    def goalie(self) -> bool:
        return self._goalie

    def type(self) -> int:
        return self._type

    def player_type(self) -> PlayerType:
        return self._player_type

    def pos(self) -> Vector2D:
        return self._pos

    def vel(self) -> Vector2D:
        return self._vel

    def body(self) -> AngleDeg:
        return self._body

    def face(self) -> AngleDeg:
        return self._face

    def recovery(self) -> float:
        return self._recovery

    def pointto_cycle(self) -> int:
        return self._pointto_cycle

    def pointto_angle(self) -> AngleDeg:
        return self._pointto_angle

    def is_pointing(self) -> bool:
        return self._pointto_cycle > 0

    def kicked(self) -> bool:
        return self._kicked

    def tackle_cycle(self) -> int:
        return self._tackle_cycle

    def is_tackling(self) -> bool:
        return self._tackle_cycle > 0

    def charged_cycle(self) -> int:
        return self._charged_cycle

    def is_charged(self):
        return self._charged_cycle > 0

    def set_team(self,
                 side: SideID,
                 unum: int,
                 goalie: bool):
        self._side = side
        self._unum = unum
        self._goalie = goalie
        if goalie:
            self._type = 0

    def set_player_type(self, type: int, player_type: PlayerType):
        self._type = type
        self._player_type = player_type

    def set_pos(self, x, y):
        self._pos.assign(x, y)

    def set_vel(self, x, y):
        self._vel.assign(x, y)

    def set_angle(self, b: AngleDeg, n: AngleDeg):
        self._body = b.copy()
        self._face = b + n

    def set_recovery(self, r: float):
        self._recovery = r

    def set_arm(self, angle: AngleDeg):
        self._pointto_cycle = 1
        self._pointto_angle = angle.copy()

    def set_kick(self, on: bool):
        self._kicked = on

    def set_tackle(self):
        self._tackle_cycle = 1

    def set_charged(self):
        self._charged_cycle = 1

    def set_card(self, card: Card):
        self._card = card

    def update(self, p):
        p: GlobalPlayerObject = GlobalPlayerObject()
        self._side = p._side
        self._unum = p._unum
        self._goalie = p._goalie

        self._pos = p._pos.copy()
        self._vel = p._vel.copy()

        self._body = p._body.copy()
        self._face = p._face.copy()

        if p.is_pointing():
            self._pointto_cycle += 1
            self._pointto_angle = p._pointto_angle.copy()
        else:
            self._pointto_cycle = 0

        self._kicked = p._kicked

        if p.is_tackling():
            self._tackle_cycle += 1
        else:
            self._tackle_cycle = 0

        if p.is_charged():
            self._charged_cycle += 1
        else:
            self._charged_cycle = 0

    def reverse(self):
        self._pos.reverse()
        self._vel.reverse()
        self._body.reverse()
        self._face.reverse()
