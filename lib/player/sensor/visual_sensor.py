from cmath import polar
from enum import Enum, auto
from lib.parser.message_params_parser_see import MessageParamsParserSee
from lib.rcsc.types import UNUM_UNKNOWN, LineID, MarkerID
from lib.rcsc.game_time import GameTime


class VisualSensor:
    DIST_ERR = float("inf")
    DIR_ERR = -360

    class ObjectType(Enum):
        Obj_Goal = 'g'
        Obj_Goal_Behind = 'G'
        Obj_Marker = 'f'
        Obj_Marker_Behind = 'F'
        Obj_Line = 'l'
        Obj_Ball = 'b'
        Obj_Player = 'p'
        Obj_Unknown = auto()

    class PlayerInfoType(Enum):
        Player_Teammate = 10
        Player_Unknown_Teammate = 11
        Player_Opponent = 20
        Player_Unknown_Opponent = 21
        Player_Unknown = 30
        Player_Low_Mode = auto()
        Player_Illegal = auto()

    class PolarT:
        def __init__(self) -> None:
            self.dist_ = VisualSensor.DIST_ERR
            self.dir_ = VisualSensor.DIR_ERR

        def reset(self):
            self.dist_ = VisualSensor.DIST_ERR
            self.dir_ = VisualSensor.DIR_ERR

        @staticmethod
        def parse_string(key, value, type):
            pass

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

        @staticmethod
        def parse_string(key, value, type, marker_map):
            marker = VisualSensor.MarkerT()
            marker.id_ = VisualSensor.ObjectType.Obj_Unknown
            if not (type == VisualSensor.ObjectType.Obj_Marker_Behind
                    or type == VisualSensor.ObjectType.Obj_Goal_Behind):
                if marker_map.get(key) is None:
                    print("No identified Marked Object!")
                    return None

                marker.id_ = marker_map[key]

            data = value.strip(" ").split(' ')
            marker.dist_ = float(data[0])
            marker.dir_ = float(data[1])

            return marker

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
        self._balls.clear()
        self._markers.clear()
        self._behind_markers.clear()
        self._lines.clear()
        self._teammates.clear()
        self._unknown_teammates.clear()
        self._opponents.clear()
        self._unknown_opponents.clear()
        self._unknown_players.clear()

    def parse(self, message: str, team_name: str, current_time: GameTime):
        if self._time == current_time:
            return
        self._time = current_time.copy()

        self.clear_all()

        object_data = MessageParamsParserSee().parse(message)
        if object_data is None:
            print("No Object have seen!")
            return

        for key, value in object_data.items():
            types = VisualSensor.ObjectType
            obj_type = types(key[0])

            if obj_type == types.Obj_Marker or obj_type == types.Obj_Goal:
                self._markers.append(VisualSensor.MarkerT.parse_string(
                    key, value, obj_type, self._marker_map))
            elif obj_type == types.Obj_Marker_Behind or obj_type == types.Obj_Goal_Behind:
                self._behind_markers.append(VisualSensor.MarkerT.parse_string(
                    key, value, obj_type, self._marker_map))
            elif obj_type == types.Obj_Player:
                player = VisualSensor.PlayerT.parse_string(
                    key, value, obj_type)
                self.add_player(player)
            elif obj_type == types.Obj_Line:
                self._lines.append(
                    VisualSensor.LineT.parse_string(key, value, obj_type))
            elif obj_type == types.Obj_Ball:
                self._balls.append(
                    VisualSensor.BallT.parse_string(key, value, obj_type))
            else:
                print(f"A seen object is not identified by its type!!")

            self.sort_all()
