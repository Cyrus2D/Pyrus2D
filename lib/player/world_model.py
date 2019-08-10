from lib.action.intercept_table import InterceptTable
from lib.player.object_player import *
from lib.player.object_ball import *
from lib.parser.parser_message_fullstate_world import FullStateWorldMessageParser
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.types import GameModeType
from lib.math.soccer_math import *


class WorldModel:
    def __init__(self):
        self._player_types = [PlayerType() for _ in range(18)]
        self._self_unum: int = 0
        self._team_name: str = ""
        self._our_side: SideID = SideID.NEUTRAL
        self._our_players = [PlayerObject() for _ in range(11)]
        self._teammates_from_ball = []
        self._opponents_from_ball = []
        self._their_players = [PlayerObject() for _ in range(11)]
        self._unknown_player = [PlayerObject() for _ in range(22)]
        self._ball: BallObject = BallObject()
        self._time: GameTime = GameTime(0, 0)
        self._intercept_table: InterceptTable = InterceptTable()
        self._game_mode: GameMode = GameMode()
        self._our_goalie_unum: int = 0
        self._last_kicker_side: SideID = SideID.NEUTRAL
        self._exist_kickable_teammates: bool = False
        self._exist_kickable_opponents: bool = False
        self._offside_line_x: float = 0
        self._offside_line_count = 0

    def ball(self) -> BallObject:
        return self._ball

    def self(self) -> PlayerObject:
        return self._our_players[self._self_unum - 1]

    def our_side(self):
        return SideID.RIGHT if self._our_side == 'r' else SideID.LEFT if self._our_side == 'l' else SideID.NEUTRAL

    def our_player(self, unum):
        return self._our_players[unum - 1]

    def their_player(self, unum):
        return self._their_players[unum - 1]

    def time(self):
        return self._time

    def parse(self, message):
        if message.find("fullstate") is not -1:
            self.fullstate_parser(message)
            self.update()
        if message.find("(init") is not -1:
            self.self_parser(message)
        elif 0 < message.find("player_type") < 3:
            self.player_type_parser(message)
        elif message.find("sense_body") is not -1:
            pass
        elif message.find("init") is not -1:
            pass

    def fullstate_parser(self, message):
        parser = FullStateWorldMessageParser()
        parser.parse(message)
        self._time._cycle = int(parser.dic()['time'])
        self._game_mode.set_game_mode(GameModeType(parser.dic()['pmode']))

        # TODO vmode counters and arm

        self._ball.init_str(parser.dic()['b'])

        for player_dic in parser.dic()['players']:
            player = PlayerObject()
            player.init_dic(player_dic)
            player.set_player_type(self._player_types[player.player_type_id()])
            if player.side().value == self._our_side:
                self._our_players[player.unum() - 1] = player
            elif player.side() == SideID.NEUTRAL:
                self._unknown_player[player.unum() - 1] = player
            else:
                self._their_players[player.unum() - 1] = player
        if self.self().side() == SideID.RIGHT:
            self.reverse()

        # print(self)

    def __repr__(self):
        # Fixed By MM _ temp
        return "(time: {})(ball: {})(tm: {})(opp: {})".format(self._time, self.ball(), self._our_players,
                                                              self._their_players)

    def self_parser(self, message: str):
        message = message.split(" ")
        self._self_unum = int(message[2])
        self._our_side = message[1]

    def player_type_parser(self, message):
        new_player_type = PlayerType()
        new_player_type.parse(message)
        self._player_types[new_player_type.id()] = new_player_type

    def reverse(self):
        self.ball().reverse()
        Object.reverse_list(self._our_players)
        Object.reverse_list(self._their_players)

    def team_name(self):
        return self._team_name

    def _update_players(self):
        for i in range(len(self._our_players)):
            if self._our_players[i].player_type() is None: continue
            self._our_players[i].update_with_world(self)
            if self._our_players[i].is_kickable():
                self._last_kicker_side = self.our_side()
                self._exist_kickable_teammates = True
        for i in range(len(self._their_players)):
            if self._their_players[i].player_type() is None: continue
            self._their_players[i].update_with_world(self)
            if self._our_players[i].is_kickable():
                self._last_kicker_side = self._their_players[i].side()
                self._exist_kickable_opponents = True

    def _update_offside_line(self):
        if not ServerParam.i().use_offside():
            self._offside_line_count = 0
            self._offside_line_x = ServerParam.i().pitch_half_length()
            return

        if (self._game_mode.mode_name() == "kick_in"
                or self._game_mode.mode_name() == "corner_kick"
                or (self._game_mode.mode_name() == "goal_kick"
                    and self._game_mode.side() == self._our_side)):
            self._offside_line_count = 0
            self._offside_line_x = ServerParam.i().pitch_half_length()
            return

        if (self._game_mode.side() != self._our_side
                and (self._game_mode.mode_name() == "goalie_catch"
                     or self._game_mode.mode_name() == "goal_kick")):
            self._offside_line_count = 0
            self._offside_line_x = ServerParam.i().their_penalty_area_line_x()
            return

        new_line = self._their_defense_line_x
        count = self._their_defense_count

        # TODO check audio memory

        self._offside_line_x = new_line
        self._offside_line_count = count

    def update(self):
        if self.time().cycle() < 1:
            return  # TODO check
        self._update_players()
        self.ball().update_with_world(self)
        self._update_offside_line()

        self._set_our_goalie_unum()  # TODO should it call here?!
        self._set_players_from_ball()

        self._intercept_table.update(self)

    def intercept_table(self):
        return self._intercept_table

    def game_mode(self):
        return self._game_mode

    def our_goalie_unum(self):
        return self._our_goalie_unum

    def _set_our_goalie_unum(self):
        for i in range(1, 12):
            tm = self.our_player(i)
            if tm is None:
                continue
            if tm.goalie():
                self._our_goalie_unum = i
                return

    def teammates_from_ball(self):
        return self._teammates_from_ball

    def opponents_from_ball(self):
        return self._opponents_from_ball

    def _set_teammates_from_ball(self):
        self._teammates_from_ball = []
        for i in range(1, 12):
            tm = self.our_player(i)
            if tm is None:
                continue

            self._teammates_from_ball.append(tm)

        self._teammates_from_ball.sort(key=lambda player: player.dist_from_ball())

    def last_kicker_side(self) -> SideID:
        return self._last_kicker_side

    def exist_kickable_opponents(self):
        return self._exist_kickable_opponents

    def exist_kickable_teammates(self):
        return self._exist_kickable_teammates

    def _set_players_from_ball(self):
        self._set_teammates_from_ball()
        self._set_opponents_from_ball()

    def _set_opponents_from_ball(self):
        self._opponents_from_ball = []
        for i in range(1, 12):
            opp = self.their_player(i)
            if opp is None:
                continue

            self._opponents_from_ball.append(opp)

        self._opponents_from_ball.sort(key=lambda player: player.dist_from_ball())

    # def offside_line_x(self) -> float:
    #     return self._offside_line_x
