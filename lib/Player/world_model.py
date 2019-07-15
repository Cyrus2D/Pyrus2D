from lib.Player.object_player import *
from lib.Player.object_ball import *
from lib.parser.parser_message_fullstate_world import FullStateWorldMessageParser
from lib.rcsc.game_time import GameTime


class WorldModel:
    def __init__(self):
        self._player_types = [PlayerType() for i in range(17)]
        self._self_unum: int = 0
        self._our_side: SideID = SideID.NEUTRAL
        self._our_players = [PlayerObject() for i in range(11)]
        self._their_players = [PlayerObject() for i in range(11)]
        self._unknown_player = [PlayerObject() for i in range(22)]
        self._ball: BallObject = BallObject()
        self._time: GameTime = GameTime(0, 0)
        self._play_mode: str = ""  # TODO should match with Play Mode ENUM

    def ball(self):
        return self._ball

    def self(self) -> PlayerObject:
        return self._our_players[self._self_unum - 1]

    def parse(self, message):
        if message.find("fullstate") is not -1:
            self.fullstate_parser(message)
        if message.find("init") is not -1:
            self.self_parser(message)
        elif message.find("player_type") is not -1:
            pass
        elif message.find("sense_body") is not -1:
            pass
        elif message.find("init") is not -1:
            pass

    def fullstate_parser(self, message):
        parser = FullStateWorldMessageParser()
        parser.parse(message)
        self._time = parser.dic()['time']
        self._play_mode = parser.dic()['pmode']

        # TODO vmode counters and arm

        self._ball.init_str(parser.dic()['b'])

        for player_dic in parser.dic()['players']:
            player = PlayerObject()
            print("player_dic", player_dic)
            player.init_dic(player_dic)
            print(player.side().value)
            print(self._our_side)
            if player.side().value == self._our_side:
                print("HERE:", player)
                self._our_players[player.unum() - 1] = player
            elif player.side() == SideID.NEUTRAL:
                self._unknown_player[player.unum() - 1] = player
            else:
                self._their_players[player.unum() - 1] = player

        print(self)

    def __repr__(self):
        # Fixed By MM _ temp
        return "(time: {})(ball: {})(tm: {})(opp: {})".format(self._time, self.ball(), self._our_players,
                                                              self._their_players)

    def self_parser(self, message: str):
        message = message.split(" ")
        self._self_unum = message[2]
        self._our_side = message[1]
