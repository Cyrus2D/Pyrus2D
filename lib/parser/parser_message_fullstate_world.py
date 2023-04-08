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
        self._kick = 0
        self._dash = 0
        self._turn = 0
        self._catch = 0
        self._move = 0
        self._turn_neck = 0
        self._change_view = 0
        self._say = 0

    def parse(self, message: str):
        self._dic['time'] = message.split(" ")[1]
        message = message[message.find("(", 1):-1]

        # before parsing players
        msg = message[:message.find("((p")]
        MessageParamsParser._parse(self._dic, msg)

        data = list(map(int, self._dic['count'].split(' ')))

        self._kick = data[0]
        self._dash = data[1]
        self._turn = data[2]
        self._catch = data[3]
        self._move = data[4]
        self._turn_neck = data[5]
        self._change_view = data[6]
        self._say = data[7]

        # and now parsing players
        msg = message[message.find("((p"):]
        self._dic.update(PlayerMessageParser().parse(msg))

    def dic(self):
        return self._dic

    def kick_count(self):
        return self._kick

    def dash_count(self):
        return self._dash

    def turn_count(self):
        return self._turn

    def catch_count(self):
        return self._catch

    def move_count(self):
        return self._move

    def turn_neck_count(self):
        return self._turn_neck

    def change_view_count(self):
        return self._change_view

    def say_count(self):
        return self._say


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
            use_point_to = 0
            if msg[3] == 'g':
                k = 1
            if msg[15 + k].find('stamina') > 0:
                use_point_to = 2
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
                    "stamina": msg[14 + k + kk + use_point_to],
                    "effort": msg[15 + k + kk + use_point_to],
                    "recovery": msg[16 + k + kk + use_point_to],
                    "capacity": msg[17 + k + kk + use_point_to].strip("()")
                },
                "focus_dist": msg[11 + k + kk + use_point_to],
                "focus_dir": msg[12 + k + kk + use_point_to].strip("()")
            }
            if use_point_to == 2:
                player_dic["pointto_dist"] = msg[10 + k].strip("()")
                player_dic["pointto_dir"] = msg[11 + k].strip("()")
            if k == 1:
                player_dic['goalie'] = 'g'
            players.append(player_dic)
            seek = next_seek
        dic["players"] = players

    @staticmethod
    def n_inner_dict(message: str):
        # dlog.debug(f"message {message}")
        n = 0
        for c in message[1:-1]:
            if c == '(':
                n += 1
        # dlog.debug(f"n {n}")
        return n

    def parse(self, message):
        PlayerMessageParser._parser(self._dic, message)
        return self._dic

# message = '(fullstate 109 (pmode play_on) (vmode high normal) (count 0 25 82 0 79 0 0 0) (arm (movable 0) (expires 0) (target 0 0) (count 0)) (score 0 0) ((b) 0 0 0 0) ((p r 10 9) 0.00733964 -23.0363 -0.399337 -0.0830174 -164.67 -90 44.2236 1.38729 (stamina 7539.49 0.935966 1 129861)) ((p r 11 10) 3.75961 -2.09864 -0.327071 0.126905 153.836 13 (stamina 7615.44 0.854839 1 129617))) '
# msg = message[message.find("((p"):]
# a =PlayerMessageParser()
# d = a.parse(msg)
# for p in d['players']:
#     debug_print(p['unum'], p['stamina'])