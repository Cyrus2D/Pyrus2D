from lib.coach.global_object import GlobalPlayerObject, GlobalBallObject
from lib.parser.global_message_parser import GlobalFullStateWorldMessageParser
from lib.player.object_player import *
from lib.player.object_ball import *
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.types import GameModeType


class GlobalWorldModel:
    def __init__(self):
        self._player_types = [PlayerType() for _ in range(18)]
        self._team_name_l: str = ""
        self._team_name_r: str = ""
        self._our_side: SideID = SideID.NEUTRAL
        self._our_players = [GlobalPlayerObject() for _ in range(11)]
        self._their_players = [GlobalPlayerObject() for _ in range(11)]
        self._unknown_player = [GlobalPlayerObject() for _ in range(22)]
        self._ball: GlobalBallObject = GlobalBallObject()
        self._time: GameTime = GameTime(0, 0)
        self._game_mode: GameMode = GameMode()
        self._last_kicker_side: SideID = SideID.NEUTRAL
        self._yellow_card_left = [False for _ in range(11)]
        self._yellow_card_right = [False for _ in range(11)]
        self._red_card_left = [False for _ in range(11)]
        self._red_card_right = [False for _ in range(11)]
        self._last_playon_start: int = 0
        # TODO add freeform allow/send count

    def ball(self) -> GlobalBallObject:
        return self._ball

    def our_side(self):
        return SideID.RIGHT if self._our_side == 'r' else SideID.LEFT if self._our_side == 'l' else SideID.NEUTRAL

    def our_player(self, unum):
        return self._our_players[unum - 1]

    def their_player(self, unum):
        return self._their_players[unum - 1]

    def time(self):
        return self._time.copy()

    def parse(self, message):
        if message.find("see_global") is not -1:
            self.fullstate_parser(message)
        elif 0 < message.find("player_type") < 3:
            self.player_type_parser(message)
        elif message.find("sense_body") is not -1:
            pass
        elif message.find("init") is not -1:
            pass

    def fullstate_parser(self, message):
        parser = GlobalFullStateWorldMessageParser()
        parser.parse(message)
        self._time._cycle = int(parser.dic()['time'])
        self._team_name_l = parser.dic()['teams']['team_left']
        self._team_name_r = parser.dic()['teams']['team_right']

        # TODO vmode counters and arm

        self._ball.init_str(parser.dic()['b'])

        if 'players' in parser.dic():
            for player_dic in parser.dic()['players']:
                player = GlobalPlayerObject()
                player.init_dic(player_dic)
                # player.set_player_type(self._player_types[player.type()])
                if player.side().value == self._our_side:
                    self._our_players[player.unum() - 1] = player
                elif player.side() == SideID.NEUTRAL:
                    self._unknown_player[player.unum() - 1] = player
                else:
                    self._their_players[player.unum() - 1] = player
            # TODO check reversion

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

    def team_name_l(self):
        return self._team_name_l

    def team_name_r(self):
        return self._team_name_r

    def game_mode(self):
        return self._game_mode

    def last_kicker_side(self) -> SideID:
        return self._last_kicker_side
