from lib.Player.player_type import *
from lib.Player.object_player import *
from lib.Player.object_ball import *

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
        """"
        (fullstate <time>
        (pmode {goalie_catch_ball_{l|r}|<play mode>})
        (vmode {high|low} {narrow|normal|high})
        //(stamina <stamina> <effort> <recovery>)
        (count <kicks> <dashes> <turns> <catches> <moves>
               <turn_necks> <change_views> <says>)
        (arm (movable <MOVABLE>) (expires <EXPIRES>)
        (target <DIST> <DIR>) (count <COUNT>))
        (score <team_points> <enemy_points>)
        ((b) <pos.x> <pos.y> <vel.x> <vel.y>)
        <players>)
        """
        """
        player: (v14)
        ((p {l | r} < unum >[g] < player_type_id >)
         < pos.x > < pos.y > < vel.x > < vel.y > < body_angle > < neck_angle > [ < point_dist > < point_dir >]
         ( < stamina > < effort > < recovery >[< capacity >])
        [t | k][y | r])
        """

        message = message[message.find("(")]
