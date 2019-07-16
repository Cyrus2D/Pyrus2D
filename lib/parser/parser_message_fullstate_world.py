from lib.parser.parser_message_params import MessageParamsParser

""""
    (fullstate <time>
    (pmod1e {goalie_catch_ball_{l|r}|<play mode>})
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


class FullStateWorldMessageParser:
    def __init__(self):
        self._dic = {}

    def parse(self, message: str):
        self._dic['time'] = message.split(" ")[1]
        message = message[message.find("(", 1):-1]

        # before parsing players
        msg = message[:message.find("((p")]
        MessageParamsParser._parse(self._dic, msg)

        # and now parsing players
        msg = message[message.find("((p"):]
        self._dic.update(PlayerMessageParser().parse(msg))

    def dic(self):
        return self._dic


class PlayerMessageParser:
    def __init__(self):
        self._dic = {}

    @staticmethod
    def _parser(dic: dict, message: str):
        players = []
        seek = 0
        while seek < len(message):
            seek = message.find("((p", seek)
            next_seek = message.find("((p", seek + 1)
            if next_seek == -1:
                next_seek = len(message)

            msg = message[seek: next_seek].strip(" ()").split(" ")
            k = 0
            kk = 0
            if msg[3] == "g":
                k = 1
            if PlayerMessageParser.n_inner_dict(message[seek: next_seek]) > 2:
                kk = 2
            player_dic = {
                "side_id": msg[1],
                "unum": msg[2],
                "player_type": msg[3 + k].strip("()"),
                "pos_x": msg[4 + k],
                "pos_y": msg[5 + k],
                "vel_x": msg[6 + k],
                "vel_y": msg[7 + k],
                "body": msg[8 + k],
                "neck": msg[9 + k],
                "stamina": {
                    "stamina": msg[11 + k + kk],
                    "effort": msg[12 + k + kk],
                    "recovery": msg[13 + k + kk],
                    "capacity": msg[14 + k + kk].strip("()")
                }
            }
            if kk == 2:
                player_dic["pointto_dist"] = msg[10 + k].strip("()")
                player_dic["pointto_dir"] = msg[11 + k].strip("()")
            if k == 1:
                player_dic['goalie'] = 'g'
            players.append(player_dic)
            seek = next_seek
        dic["players"] = players

    @staticmethod
    def n_inner_dict(message: str):
        print("message", message)
        n = 0
        for c in message[1:-1]:
            if c == '(':
                n += 1
        print("n", n)
        return n


    def parse(self, message):
        PlayerMessageParser._parser(self._dic, message)
        return self._dic

