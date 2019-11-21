from lib.action.intercept_table import InterceptTable
from lib.player.object_player import *
from lib.player.object_ball import *
from lib.parser.parser_message_fullstate_world import FullStateWorldMessageParser
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.types import GameModeType
from lib.math.soccer_math import *
from typing import List


class WorldModel:
    def __init__(self):
        self._player_types = [PlayerType() for _ in range(18)]
        self._self_unum: int = None
        self._team_name: str = ""
        self._our_side: SideID = SideID.NEUTRAL
        self._our_players = [PlayerObject() for _ in range(11)]
        self._teammates_from_ball: List[PlayerObject] = []
        self._opponents_from_ball: List[PlayerObject] = []
        self._teammates_from_self: List[PlayerObject] = []
        self._opponents_from_self: List[PlayerObject] = []
        self._their_players = [PlayerObject() for _ in range(11)]
        self._unknown_player = [PlayerObject() for _ in range(22)]
        self._ball: BallObject = BallObject()
        self._time: GameTime = GameTime(0, 0)
        self._intercept_table: InterceptTable = InterceptTable()
        self._game_mode: GameMode = GameMode()
        self._our_goalie_unum: int = 0
        self._their_goalie_unum: int = 0
        self._last_kicker_side: SideID = SideID.NEUTRAL
        self._exist_kickable_teammates: bool = False
        self._exist_kickable_opponents: bool = False
        self._offside_line_x: float = 0
        self._offside_line_count = 0
        self._their_defense_line_x: float = 0
        self._their_defense_line_count = 0

    def ball(self) -> BallObject:
        return self._ball

    def self(self) -> PlayerObject:
        if self.self_unum():
            return self._our_players[self._self_unum - 1]
        else:
            return None

    def our_side(self):
        return SideID.RIGHT if self._our_side == 'r' else SideID.LEFT if self._our_side == 'l' else SideID.NEUTRAL

    def our_player(self, unum):
        return self._our_players[unum - 1]

    def their_player(self, unum):
        return self._their_players[unum - 1]

    def time(self):
        return self._time.copy()

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

    def self_parser(self, message):
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
        self._exist_kickable_teammates = False
        self._exist_kickable_opponents = False
        for i in range(len(self._our_players)):
            if self._our_players[i].player_type() is None:
                continue
            self._our_players[i].update_with_world(self)
            if self._our_players[i].is_kickable():
                self._last_kicker_side = self.our_side()
                if i != self.self().unum():
                    self._exist_kickable_teammates = True
        for i in range(len(self._their_players)):
            if self._their_players[i].player_type() is None:
                continue
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
        count = self._their_defense_line_count

        # TODO check audio memory

        self._offside_line_x = new_line
        self._offside_line_count = count

    def update(self):
        if self.time().cycle() < 1:
            return  # TODO check
        self._update_players()
        self.ball().update_with_world(self)

        self._set_goalies_unum()  # TODO should it call here?!
        self._set_players_from_ball_and_self()

        self._update_their_defense_line()
        self._update_offside_line()

        self._intercept_table.update(self)

    def _update_their_defense_line(self):
        speed_rate = ServerParam.i().default_player_speed_max() * (0.8
                                                                   if self.ball().vel().x() < -1
                                                                   else 0.25)
        first, second = 0, 0
        first_count, second_count = 1000, 1000

        for it in self._opponents_from_ball:
            x = it.pos().x()
            if it.vel_count() <= 1 and it.vel().x() > 0:
                x += min(0.8, it.vel().x() / it.player_type().player_decay())
            elif it.body_count() <= 3 and it.body().abs() < 100:
                x -= speed_rate * min(10, it.pos_count() - 1.5)
            else:
                x -= speed_rate * min(10, it.pos_count())

            if x > second:
                second = x
                second_count = it.pos_count()
                if second > first:
                    # swap
                    first, second = second, first
                    first_count, second_count = second_count, first_count
        new_line = second
        count = second_count

        goalie = self.get_opponent_goalie()
        if goalie is None:
            if 20 < self.ball().pos().x() < ServerParam.i().their_penalty_area_line_x():
                if first < ServerParam.i().their_penalty_area_line_x():
                    new_line = first
                    count = 30

        if len(self._opponents_from_self) >= 11:
            pass
        elif new_line < self._their_defense_line_x - 13:
            pass
        elif new_line < self._their_defense_line_x - 5:
            new_line = self._their_defense_line_x - 1

        if new_line < 0:
            new_line = 0

        if (self._game_mode.mode_name() != "before_kick_off"
                and self._game_mode.mode_name() != "after_goal"
                and self.ball().pos_count() <= 3):
            ball_next = self.ball().pos() + self.ball().vel()
            if ball_next.x() > new_line:
                new_line = ball_next.x()
                count = self.ball().pos_count()
        self._their_defense_line_x = new_line
        self._their_defense_line_count = count

    def intercept_table(self):
        return self._intercept_table

    def game_mode(self):
        return self._game_mode

    def our_goalie_unum(self):
        return self._our_goalie_unum

    def their_goalie_unum(self):
        return self._their_goalie_unum

    def get_opponent_goalie(self):
        return self.their_player(self._their_goalie_unum)

    def _set_goalies_unum(self):
        for tm in self._our_players:
            if tm is None:
                continue
            if tm.goalie():
                self._our_goalie_unum = tm.unum()
                break

        for opp in self._their_players:
            if opp is None:
                continue
            if opp.goalie():
                self._their_goalie_unum = opp.unum()
                break

    def teammates_from_ball(self):
        return self._teammates_from_ball

    def opponents_from_ball(self):
        return self._opponents_from_ball

    def _set_teammates_from_ball(self):
        self._teammates_from_ball = []
        for tm in self._our_players:
            if tm is None or tm.unum() == self._self_unum:
                continue

            self._teammates_from_ball.append(tm)

        self._teammates_from_ball.sort(key=lambda player: player.dist_from_ball())

    def last_kicker_side(self) -> SideID:
        return self._last_kicker_side

    def exist_kickable_opponents(self):
        return self._exist_kickable_opponents

    def exist_kickable_teammates(self):
        return self._exist_kickable_teammates

    def _set_players_from_ball_and_self(self):
        self._set_teammates_from_ball()
        self._set_opponents_from_ball()
        self._set_teammates_from_self()
        self._set_opponents_from_self()

    def _set_teammates_from_self(self):
        self._teammates_from_self = []
        for tm in self._our_players:
            if tm is None or tm.unum() == self._self_unum:
                continue

            self._teammates_from_self.append(tm)

        self._teammates_from_self.sort(key=lambda player: player.dist_from_self())

    def _set_opponents_from_self(self):
        self._opponents_from_self = []
        for opp in self._their_players:
            if opp is None:
                continue

            self._opponents_from_self.append(opp)

        self._opponents_from_self.sort(key=lambda player: player.dist_from_self())

    def _set_opponents_from_ball(self):
        self._opponents_from_ball = []
        for opp in self._their_players:
            if opp is None:
                continue

            self._opponents_from_ball.append(opp)

        self._opponents_from_ball.sort(key=lambda player: player.dist_from_ball())

    def offside_line_x(self) -> float:
        return self._offside_line_x

    def get_opponent_nearest_to_self(self,
                                     count_thr: int,
                                     with_goalie: bool = True) -> PlayerObject:
        return self.get_first_player(self._opponents_from_self,
                                     count_thr,
                                     with_goalie)

    def get_first_player(self,
                         players: list,
                         count_thr: int,
                         with_goalie: bool) -> PlayerObject:
        for p in players:
            if not with_goalie and p.goalie():
                continue

            if not p.is_ghost() and p.pos_count() <= count_thr:
                return p

        return None

    def self_unum(self):
        return self._self_unum
