from lib.Player.player_type import *







class WorldModel:
    def __init__(self):
        self.player_types = [PlayerType() for i in range(17)]
        self.self_unum = 0
        self.our_side = -1
        self.our_players = [PlayerObject() for i in range(11)]
        self.their_players = [PlayerObject() for i in range(11)]
        self.ball = BallObject()

    def parse(self, message):
        if message.find("fullstate") is not -1:
            pass
        elif message.find("player_type") is not -1:
            pass
        elif message.find("sense_body") is not -1:
            pass
        elif message.find("init") is not -1:
            pass
