from lib.parser.parser_message_params import MessageParamsParser

"""
    sample version >= 7.0
    (see_global TIME ((g l) -52.5 0) ((g r) 52.5 0) ((b) <x> <y> <vx> <vy>)
       ((p "TEAM" UNUM[ goalie]) <x> <y> <vx> <vy> <body> <neck>[ <arm>][ {t|k}][ {y|r}])
       ....)
        <-- arm is global
        <-- 't' means tackle
        <-- 'k' means kick
        <-- 'f' means foul charged
        <-- 'y' means yellow card
        <-- 'r' means red card
    (ok look TIME ((g l) -52.5 0) ((g r) 52.5 0) ((b) <x> <y> <vx> <vy>)
       ((p "TEAM" UNUM[ goalie]) <x> <y> <vx> <vy> <body> <neck>) <-- no arm & tackle
       ....)
   
"""


class GlobalFullStateWorldMessageParser:
    def __init__(self):
        self._dic = {}

    def parse(self, message: str):
        self._dic['time'] = message.split(" ")[1]
        message = message[message.find("(", 1):-1]

        # parsing ball
        msg = message[:message.find("((p")]
        MessageParamsParser._parse(self._dic, msg)

        # and now parsing players
        msg = message[message.find("((p"):]
        self._dic.update(PlayerMessageParser().parse(msg))
        self._dic.update({"teams": {
            "team_left": PlayerMessageParser._team_l,
            "team_right": PlayerMessageParser._team_r
        }})

    def dic(self):
        return self._dic


class PlayerMessageParser:
    _team_l = None
    _team_r = None

    def __init__(self):
        self._dic = {}

    @staticmethod
    def _parser(dic: dict, message: str):
        players = []
        seek = 0
        if len(message) < 5:
            return
        while seek < len(message):
            seek = message.find("((p", seek)
            next_seek = message.find("((p", seek + 1)

            if next_seek == -1:
                next_seek = len(message)
            msg = message[seek: next_seek].strip(" ()").split(" ")
            k = -1
            kk = 0
            if msg[3] == 'g' or msg[3] == 'goalie)':
                k = 0
            player_dic = {
                "unum": msg[2].strip("()"),
                "pos_x": msg[4 + k],
                "pos_y": msg[5 + k],
                "vel_x": msg[6 + k],
                "vel_y": msg[7 + k],
                "body": msg[8 + k],
                "neck": msg[9 + k],
            }
            if PlayerMessageParser._team_l == msg[1]:
                player_dic['side_id'] = 'l'
            elif PlayerMessageParser._team_r == msg[1]:
                player_dic['side_id'] = 'r'
            elif PlayerMessageParser._team_l is None:
                PlayerMessageParser._team_l = msg[1]
                player_dic['side_id'] = 'l'
            elif PlayerMessageParser._team_r is None:
                PlayerMessageParser._team_r = msg[1]
                player_dic['side_id'] = 'r'

            if k == 0:
                player_dic['goalie'] = 'g'
            ext = []
            if ((k == 0 and len(msg) > 10)
                    or (k == -1 and len(msg) > 9)):
                ext = msg[10 + k:]
            if 'k' in ext:
                player_dic['kick'] = True
            if 't' in ext:
                player_dic['tackle'] = True
            if 'f' in ext:
                player_dic['charged'] = True
            if 'y' in ext:
                player_dic['card'] = 'y'
            if 'r' in ext:
                player_dic['card'] = 'r'

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
