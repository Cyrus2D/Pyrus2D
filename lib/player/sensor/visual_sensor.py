from enum import Enum, auto

from lib.debug.debug import log
from lib.parser.message_params_parser_see import MessageParamsParserSee
from lib.rcsc.types import UNUM_UNKNOWN, LineID, MarkerID
from lib.rcsc.game_time import GameTime


class SeeParser:
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
            self.dist_: float = SeeParser.DIST_ERR
            self.dir_: float = SeeParser.DIR_ERR

        def reset(self):
            self.dist_ = SeeParser.DIST_ERR
            self.dir_ = SeeParser.DIR_ERR

        @staticmethod
        def parse_string(key, value):
            pass

        def __repr__(self) -> str:
            res = "{"
            for k, v in self.__dict__.items():
                res += f"{k}:{v},"
            res = res[:-1] + "}"
            return res

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

        @staticmethod
        def parse_string(key, value):
            line = SeeParser.LineT()
            line_name = key.split(' ')[1]

            line.id_ = LineID(line_name)

            state_data = value.split(" ")
            line.dist_ = float(state_data[0])
            line.dir_ = float(state_data[1])

            return line

    class MarkerT(PolarT):
        def __init__(self) -> None:
            super().__init__()
            self.object_type_ = SeeParser.ObjectType.Obj_Unknown
            self.id_ = MarkerID.Marker_Unknown

        def reset(self):
            super().reset()
            self.object_type_ = SeeParser.ObjectType.Obj_Unknown
            self.id_ = MarkerID.Marker_Unknown

        def __str__(self):
            return f'Marker {self.id_} {self.object_type_} {self.dist_} {self.dir_}'

        @staticmethod
        def parse_string(key, value, type, marker_map):
            marker = SeeParser.MarkerT()
            marker.id_ = SeeParser.ObjectType.Obj_Unknown
            marker.object_type_ = type

            if not (type == SeeParser.ObjectType.Obj_Marker_Behind
                    or type == SeeParser.ObjectType.Obj_Goal_Behind):
                if marker_map.get(key) is None:
                    log.os_log().error("No identified Marked Object!")
                    return None

                marker.id_ = marker_map[key]

            data = value.strip(" ").split(' ')
            marker.dist_ = float(data[0])
            marker.dir_ = float(data[1])

            return marker

    class BallT(MoveableT):
        def __init__(self) -> None:
            super().__init__()

        @staticmethod
        def parse_string(key, value):
            ball = SeeParser.BallT()

            state_data = value.split(" ")
            n_state_data = len(state_data)

            ball.dist_ = float(state_data[0])
            ball.dir_ = float(state_data[1])

            if n_state_data == 4:
                ball.dist_chng_ = float(state_data[2])
                ball.dir_chng_ = float(state_data[3])
                ball.has_vel_ = True
            return ball

    class PlayerT(MoveableT):
        def __init__(self) -> None:
            super().__init__()
            self.unum_ = UNUM_UNKNOWN
            self.goalie_: bool = False
            self.body_ = SeeParser.DIR_ERR
            self.face_ = SeeParser.DIR_ERR
            self.arm_ = SeeParser.DIR_ERR
            self.kicking_: bool = False
            self.tackle_: bool = False

        def reset(self):
            super().reset()
            self.unum_ = UNUM_UNKNOWN
            self.goalie_: bool = False
            self.body_ = SeeParser.DIR_ERR
            self.face_ = SeeParser.DIR_ERR
            self.arm_ = SeeParser.DIR_ERR
            self.kicking_: bool = False
            self.tackle_: bool = False

        @staticmethod
        def parse_string(key, value, team_name, visual_sensor):
            # PARSE KEY
            types = SeeParser.PlayerInfoType

            player = SeeParser.PlayerT()
            result_type = types.Player_Illegal

            player_data = key.split(" ")
            n_player_data = len(player_data)

            if n_player_data >= 2:
                player_data[1] = player_data[1].strip('"')
                if player_data[1] == team_name:
                    result_type = types.Player_Unknown_Teammate
                else:
                    result_type = types.Player_Unknown_Opponent
                    if visual_sensor._their_team_name is None:
                        visual_sensor._their_team_name = player_data[1]
            else:
                result_type = types.Player_Unknown

            if n_player_data >= 3:
                player.unum_ = int(player_data[2])
                result_type = (types.Player_Teammate
                               if result_type == types.Player_Unknown_Teammate
                               else types.Player_Opponent)

            else:
                player.unum_ = UNUM_UNKNOWN

            if n_player_data == 4:
                player.goalie_ = True

            # PARSE VALUE
            state_data = value.split(" ")
            n_state_data = len(state_data)

            if n_state_data >= 5:
                player.dist_ = float(state_data[0])
                player.dir_ = float(state_data[1])
                player.dist_chng_ = float(state_data[2])
                player.dir_chng_ = float(state_data[3])
                player.body_ = float(state_data[4])
                player.has_vel_ = True

                if n_state_data >= 6:
                    player.face_ = float(state_data[5])

                if n_state_data == 8:
                    player.arm_ = float(state_data[6])
                    if state_data[7] == 'k':
                        player.kicking_ = True
                    if state_data[7] == 't':
                        player.tackle_ = True

                elif n_state_data == 7:
                    if state_data[-1] == 'k':
                        player.kicking_ = True
                    elif state_data[-1] == 't':
                        player.tackle_ = True
                    else:
                        player.arm_ = float(state_data[-1])

            elif n_state_data >= 2:
                player.dist_ = float(state_data[0])
                player.dir_ = float(state_data[1])

                if n_state_data == 4:
                    if state_data[-1] == 't':
                        player.tackle_ = True
                        player.arm_ = float(state_data[-2])
                    elif state_data[-1] == 'k':
                        player.kicking_ = True
                        player.arm_ = float(state_data[-2])
                    else:
                        player.dist_chng_ = float(state_data[2])
                        player.dir_chng_ = float(state_data[3])
                        player.has_vel_ = True
                elif n_state_data == 3:
                    if state_data[-1] == 'k':
                        player.kicking_ = True
                    elif state_data[-1] == 't':
                        player.tackle_ = True
                    else:
                        player.arm_ = float(state_data[-1])

            elif n_state_data == 1:
                player.dir_ = float(state_data[0])

            return player, result_type

    def __init__(self) -> None:
        self._time: GameTime = GameTime()
        self._their_team_name: str = None
        self._marker_map: dict[str, MarkerID] = {}

        self._balls: list[SeeParser.BallT] = []
        self._markers: list[SeeParser.MarkerT] = []
        self._behind_markers: list[SeeParser.MarkerT] = []
        self._lines: list[SeeParser.LineT] = []
        self._teammates: list[SeeParser.PlayerT] = []
        self._unknown_teammates: list[SeeParser.PlayerT] = []
        self._opponents: list[SeeParser.PlayerT] = []
        self._unknown_opponents: list[SeeParser.PlayerT] = []
        self._unknown_players: list[SeeParser.PlayerT] = []

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

    def add_player(self, player, player_type):
        types = SeeParser.PlayerInfoType
        if player_type == types.Player_Teammate:
            self._teammates.append(player)
        elif player_type == types.Player_Unknown_Teammate:
            self._unknown_teammates.append(player)
        elif player_type == types.Player_Opponent:
            self._opponents.append(player)
        elif player_type == types.Player_Unknown_Opponent:
            self._unknown_opponents.append(player)
        elif player_type == types.Player_Unknown:
            self._unknown_players.append(player)

    def sort_all(self):
        def dist_lambda(a): return a.dist_
        self._teammates.sort(key=dist_lambda)
        self._unknown_teammates.sort(key=dist_lambda)
        self._opponents.sort(key=dist_lambda)
        self._unknown_opponents.sort(key=dist_lambda)
        self._unknown_players.sort(key=dist_lambda)
        self._markers.sort(key=dist_lambda)
        self._behind_markers.sort(key=dist_lambda)
        self._lines.sort(key=dist_lambda)

    def parse(self, message: str, team_name: str, current_time: GameTime):
        if self._time == current_time:
            return
        self._time = current_time.copy()

        self.clear_all()

        object_data = MessageParamsParserSee().parse(message)
        if object_data is None:
            log.os_log().warn("No Object have seen!")
            return
        for key_value in object_data:
            key = key_value[0]
            value = key_value[1]
            types = SeeParser.ObjectType
            t: str = key[0]
            if t in ['P', 'B', 'L']:
                t = t.lower()
            obj_type = types(t)
            
            value = value.strip(")")

            if obj_type == types.Obj_Marker or obj_type == types.Obj_Goal:
                self._markers.append(SeeParser.MarkerT.parse_string(
                    key, value, obj_type, self._marker_map))
            elif obj_type == types.Obj_Marker_Behind or obj_type == types.Obj_Goal_Behind:
                self._behind_markers.append(SeeParser.MarkerT.parse_string(
                    key, value, obj_type, self._marker_map))
            elif obj_type == types.Obj_Player:
                player, player_type = SeeParser.PlayerT.parse_string(
                    key, value, team_name, self)
                self.add_player(player, player_type)
            elif obj_type == types.Obj_Line:
                self._lines.append(
                    SeeParser.LineT.parse_string(key, value))
            elif obj_type == types.Obj_Ball:
                self._balls.append(
                    SeeParser.BallT.parse_string(key, value))
            else:
                log.os_log().error(f"A seen object is not identified by its type!!")

            self.sort_all()

    def __str__(self):
        res = "\n"
        res += "-"*50 + '\n'
        res += "teammates: \n".upper()
        res += "\n".join(map(str, self._teammates))
        res += "\n" + "-"*50 + "\nunknown_teammates: \n".upper()
        res += "\n".join(map(str, self._unknown_teammates))
        res += "\n" + "-"*50 + "\nopponents: \n".upper()
        res += "\n".join(map(str, self._opponents))
        res += "\n" + "-"*50 + "\nunknown_opponents: \n".upper()
        res += "\n".join(map(str, self._unknown_opponents))
        res += "\n" + "-"*50 + "\nunknown_players: \n".upper()
        res += "\n".join(map(str, self._unknown_players))
        res += "\n" + "-"*50 + "\nmarkers: \n".upper()
        res += "\n".join(map(str, self._markers))
        res += "\n" + "-"*50 + "\nbehind_markers: \n".upper()
        res += "\n".join(map(str, self._behind_markers))
        res += "\n" + "-"*50 + "\nlines: \n".upper()
        res += "\n".join(map(str, self._lines))
        return res

    def time(self):
        return self._time

    def their_team_name(self):
        return self._their_team_name

    def marker_map(self):
        return self._marker_map

    def balls(self):
        return self._balls

    def markers(self):
        return self._markers

    def behind_markers(self):
        return self._behind_markers

    def lines(self):
        return self._lines

    def teammates(self):
        return self._teammates

    def unknown_teammates(self):
        return self._unknown_teammates

    def opponents(self):
        return self._opponents

    def unknown_opponents(self):
        return self._unknown_opponents

    def unknown_players(self):
        return self._unknown_players
