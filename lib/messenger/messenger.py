from enum import Enum
from typing import TYPE_CHECKING

from lib.debug.debug import log
from lib.debug.level import Level
from pyrusgeom.vector_2d import Vector2D
from lib.messenger.messenger_memory import MessengerMemory
from lib.rcsc.game_time import GameTime

from lib.rcsc.server_param import ServerParam
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel


class Messenger:
    DEBUG = True

    class Types(Enum):
        BALL = 'b'
        PASS = 'p'
        NONE = ''
        BALL_PLAYER = 'B'
        BALL_GOALIE = 'G'
        GOALIE_PLAYER = 'e'
        GOALIE = 'g'
        THREE_PLAYER = 'R'
        TWO_PLAYER = 'Q'
        ONE_PLAYER = 'P'



    SIZES: dict[Types, int] = {
        Types.BALL: 6,
        Types.PASS: 10,
        Types.BALL_PLAYER: 10,
        Types.BALL_GOALIE: 10,
        Types.GOALIE_PLAYER: 8,
        Types.GOALIE: 5,
        Types.THREE_PLAYER: 10,
        Types.TWO_PLAYER: 7,
        Types.ONE_PLAYER: 4,

    }

    def __init__(self, message: str = None) -> None:
        self._type: Messenger.Types = Messenger.Types.NONE
        self._size: int = 0
        self._message: str = message
        self._header: str = None

    def encode(self, wm: 'WorldModel') -> str:
        pass

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        pass

    def size(self):
        return self._size

    def type(self):
        return self._type

    @staticmethod
    def encode_all(wm: 'WorldModel', messages: list['Messenger']):
        max_message_size = ServerParam.i().player_say_msg_size()
        size = 0
        all_messages = ""
        for i, message in enumerate(messages):
            enc = message.encode(wm)
            log.os_log().debug(f'enc: {enc}')

            if not enc:
                continue

            if len(enc) + size > max_message_size:
                log.os_log().warn("(Messenger encode all) out of limitation. Deny other messages.")
                log.os_log().warn("denied messages are:")
                for denied in messages[i:]:
                    log.os_log().warn(denied)
                break

            if Messenger.DEBUG:
                log.sw_log().action().add_text( f"(encode all messages) a message added, msg={message}, encoded={enc}")

            all_messages += enc
            size += len(enc)
        return all_messages

    @staticmethod
    def decode_all(messenger_memory: MessengerMemory, messages: str, sender: int, current_time: GameTime):
        from lib.messenger.ball_pos_vel_messenger import BallPosVelMessenger
        from lib.messenger.player_pos_unum_messenger import PlayerPosUnumMessenger
        from lib.messenger.pass_messenger import PassMessenger

        messenger_classes: dict[Messenger.Types, type['Messenger']] = {
            Messenger.Types.BALL_POS_VEL_MESSAGE: BallPosVelMessenger,
            Messenger.Types.PLAYER_POS_VEL_UNUM: PlayerPosUnumMessenger,
            Messenger.Types.PASS: PassMessenger,
        }

        index = 0
        while index < len(messages):
            message_type = Messenger.Types(messages[index])
            message_size = Messenger.SIZES[message_type]

            message = messages[index: index+message_size]

            messenger_classes[message_type](message=message).decode(messenger_memory, sender, current_time)
            index += message_size




