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
            player.init_dic(player_dic)
            if player.side() == self.self().side():
                self._our_players.append(player)
            else:
                self._their_players.append(player)

        print(self)

    def __repr__(self):
        print(self._our_players) # Fixed By MM _ temp
        return "time: {}, ball: {}, tm: {}, opp: {}".format(self._time, self.ball(), self._our_players,
                                                            self._their_players)
