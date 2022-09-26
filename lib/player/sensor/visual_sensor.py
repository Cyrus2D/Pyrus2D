from cmath import polar
from enum import Enum, auto
from lib.rcsc.types import UNUM_UNKNOWN, LineID, MarkerID
from lib.rcsc.game_time import GameTime


class VisualSensor:
    DIST_ERR = float("inf")
    DIR_ERR = -360

    class ObjectType(Enum):
        Obj_Goal = auto()
        Obj_Goal_Behind = auto()
        Obj_Marker = auto()
        Obj_Marker_Behind = auto()
        Obj_Line = auto()
        Obj_Ball = auto()
        Obj_Player = auto()
        Obj_Unknown = auto()

    class PlayerInfoType:
        Player_Teammate = 10
        Player_Unknown_Teammate = 11
        Player_Opponent = 20
        Player_Unknown_Opponent = 21
        Player_Unknown = 30
        Player_Low_Mode = auto()
        Player_Illegal = auto()

    class PolarT:
        def __init__(self) -> None:
            self.dist = VisualSensor.DIST_ERR
            self.dir = VisualSensor.DIR_ERR

        def reset(self):
            self.dist_ = VisualSensor.DIST_ERR
            self.dir_ = VisualSensor.DIR_ERR

    class MoveableT(PolarT):
        def __init__(self) -> None:
            super().__init__()
            self.has_vel_ = False
            self.dist_chng_ = 0.
            self.dir_chng_ = 0.

        def reset(self):
            super().reset()
            self.has_vel_ = False
            self.dist_chng_ = 0.
            self.dir_chng_ = 0.

    class LineT(PolarT):
        def __init__(self) -> None:
            super().__init__()
            self.id_ = LineID.Line_Unknown

        def reset(self):
            super().reset()
            self.id_ = LineID.Line_Unknown

    class MarkerT(PolarT):
        def __init__(self) -> None:
            super().__init__()
            self.object_type_ = VisualSensor.ObjectType.Obj_Unknown
            self.id_ = MarkerID.Marker_Unknown

        def reset(self):
            super().reset()
            self.object_type_ = VisualSensor.ObjectType.Obj_Unknown
            self.id_ = MarkerID.Marker_Unknown

    class BallT(PolarT):
        def __init__(self) -> None:
            super().__init__()

    class PlayerT(MoveableT):
        def __init__(self) -> None:
            super().__init__()
            self.unum_ = UNUM_UNKNOWN
            self.goalie: bool = False
            self.body_ = VisualSensor.DIR_ERR
            self.face_ = VisualSensor.DIR_ERR
            self.arm_ = VisualSensor.DIR_ERR
            self.kicking_: bool = False
            self.tackle_: bool = False

        def reset(self):
            super().reset()
            self.unum_ = UNUM_UNKNOWN
            self.goalie: bool = False
            self.body_ = VisualSensor.DIR_ERR
            self.face_ = VisualSensor.DIR_ERR
            self.arm_ = VisualSensor.DIR_ERR
            self.kicking_: bool = False
            self.tackle_: bool = False

    def __init__(self) -> None:
        self._time: GameTime
        self._their_team_name: str
        self._marker_map: dict[str, MarkerID]

        self._balls: list[VisualSensor.BallT] = []
        self._markers: list[VisualSensor.MarkerT] = []
        self._behind_markers: list[VisualSensor.MarkerT] = []
        self._lines: list[VisualSensor.LineT] = []
        self._teammates: list[VisualSensor.PlayerT] = []
        self._unknown_teammates: list[VisualSensor.PlayerT] = []
        self._opponents: list[VisualSensor.PlayerT] = []
        self._unknown_opponents: list[VisualSensor.PlayerT] = []
        self._unknown_players: list[VisualSensor.PlayerT] = []
        
        self.initial_marker_map()
    
    def initial_marker_map(self):
        self._marker_map["g l"] = MarkerID.Goal_L
        self._marker_map["g r"] = MarkerID.Goal_R
        self._marker_map["f c"] = MarkerID.Flag_C
        self._marker_map["f c t"] = MarkerID.Flag_CT
        self._marker_map["f c b"] = MarkerID.Flag_CB
        self._marker_map["f l t"] = MarkerID.Flag_LT
        self._marker_map["f l b"] = MarkerID.Flag_LB
        self._marker_map["f r t"] = MarkerID.Flag_RT
        self._marker_map["f r b"] = MarkerID.Flag_RB
        self._marker_map["f p l t"] = MarkerID.Flag_PLT
        self._marker_map["f p l c"] = MarkerID.Flag_PLC
        self._marker_map["f p l b"] = MarkerID.Flag_PLB
        self._marker_map["f p r t"] = MarkerID.Flag_PRT
        self._marker_map["f p r c"] = MarkerID.Flag_PRC
        self._marker_map["f p r b"] = MarkerID.Flag_PRB
        self._marker_map["f g l t"] = MarkerID.Flag_GLT
        self._marker_map["f g l b"] = MarkerID.Flag_GLB
        self._marker_map["f g r t"] = MarkerID.Flag_GRT
        self._marker_map["f g r b"] = MarkerID.Flag_GRB
        self._marker_map["f t l 50"] = MarkerID.Flag_TL50
        self._marker_map["f t l 40"] = MarkerID.Flag_TL40
        self._marker_map["f t l 30"] = MarkerID.Flag_TL30
        self._marker_map["f t l 20"] = MarkerID.Flag_TL20
        self._marker_map["f t l 10"] = MarkerID.Flag_TL10
        self._marker_map["f t 0"] = MarkerID.Flag_T0
        self._marker_map["f t r 10"] = MarkerID.Flag_TR10
        self._marker_map["f t r 20"] = MarkerID.Flag_TR20
        self._marker_map["f t r 30"] = MarkerID.Flag_TR30
        self._marker_map["f t r 40"] = MarkerID.Flag_TR40
        self._marker_map["f t r 50"] = MarkerID.Flag_TR50
        self._marker_map["f b l 50"] = MarkerID.Flag_BL50
        self._marker_map["f b l 40"] = MarkerID.Flag_BL40
        self._marker_map["f b l 30"] = MarkerID.Flag_BL30
        self._marker_map["f b l 20"] = MarkerID.Flag_BL20
        self._marker_map["f b l 10"] = MarkerID.Flag_BL10
        self._marker_map["f b 0"] = MarkerID.Flag_B0
        self._marker_map["f b r 10"] = MarkerID.Flag_BR10
        self._marker_map["f b r 20"] = MarkerID.Flag_BR20
        self._marker_map["f b r 30"] = MarkerID.Flag_BR30
        self._marker_map["f b r 40"] = MarkerID.Flag_BR40
        self._marker_map["f b r 50"] = MarkerID.Flag_BR50
        self._marker_map["f l t 30"] = MarkerID.Flag_LT30
        self._marker_map["f l t 20"] = MarkerID.Flag_LT20
        self._marker_map["f l t 10"] = MarkerID.Flag_LT10
        self._marker_map["f l 0"] = MarkerID.Flag_L0
        self._marker_map["f l b 10"] = MarkerID.Flag_LB10
        self._marker_map["f l b 20"] = MarkerID.Flag_LB20
        self._marker_map["f l b 30"] = MarkerID.Flag_LB30
        self._marker_map["f r t 30"] = MarkerID.Flag_RT30
        self._marker_map["f r t 20"] = MarkerID.Flag_RT20
        self._marker_map["f r t 10"] = MarkerID.Flag_RT10
        self._marker_map["f r 0"] = MarkerID.Flag_R0
        self._marker_map["f r b 10"] = MarkerID.Flag_RB10
        self._marker_map["f r b 20"] = MarkerID.Flag_RB20
        self._marker_map["f r b 30"] = MarkerID.Flag_RB30
    
    def clear_all(self):
        self._balls = []
        self._markers = []
        self._behind_markers = []
        self._lines = []
        self._teammates = []
        self._unknown_teammates = []
        self._opponents = []
        self._unknown_opponents = []
        self._unknown_players = []