from lib.parser.parser_message_params import MessageParamsParser


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
        print(self._dic)


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

            msg = message[seek: next_seek].strip("()").split(" ")
            player_dic = {
                "side_id": msg[1],
                "unum": msg[2],
                "player_type": msg[3].strip("()"),
                "pos_x": msg[4],
                "pos_y": msg[5],
                "vel_x": msg[6],
                "vel_y": msg[7],
                "body": msg[8],
                "neck": msg[9],
                "stamina": {
                    "stamina": msg[11],
                    "effort": msg[12],
                    "recovery": msg[13],
                    "capacity": msg[14].strip("()")
                }
            }
            players.append(player_dic)
            seek = next_seek
        dic["players"] = players

    def parse(self, message):
        PlayerMessageParser._parser(self._dic, message)
        return self._dic
