from lib.Player.player_type import *
from lib.Player.object_player import *
from lib.Player.object_ball import *
from lib.parser.parser_message_fullstate_world import FullStateWorldMessageParser

import lib.server_param as SP


class WorldModel:
    def __init__(self):
        self.player_types = [PlayerType() for i in range(17)]
        self.self_unum = 0
        self.our_side = -1
        self.our_players = [PlayerObject() for i in range(11)]
        self.their_players = [PlayerObject() for i in range(11)]
        self.ball = BallObject()

    def ball(self):
        return self.ball

    def self(self):
        return self.our_players[self.self_unum - 1]

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


