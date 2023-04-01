from enum import Enum, unique
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
        RECOVERY = 'r'
        STAMINA = 's'


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
        Types.RECOVERY: 2,
        Types.STAMINA: 2,

    }

    def __init__(self, message: str = None) -> None:
        self._type: Messenger.Types = Messenger.Types.NONE
        self._size: int = 0
        self._message: str = message
        self._header: str = None

    def encode(self) -> str:
        pass

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        pass

    def size(self):
        return self._size

    def type(self):
        return self._type

    @staticmethod
    def encode_all(messages: list['Messenger']):
        max_message_size = ServerParam.i().player_say_msg_size()
        size = 0
        all_messages = ""
        log.os_log().debug(f'#'*20)
        for i, message in enumerate(messages):
            log.os_log().debug(f'msg.t={message._header}')
            enc = message.encode()
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
        from lib.messenger.pass_messenger import PassMessenger
        from lib.messenger.ball_goalie_messenger import BallGoalieMessenger
        from lib.messenger.ball_messenger import BallMessenger
        from lib.messenger.ball_player_messenger import BallPlayerMessenger
        from lib.messenger.goalie_messenger import GoalieMessenger
        from lib.messenger.goalie_player_messenger import GoaliePlayerMessenger
        from lib.messenger.one_player_messenger import OnePlayerMessenger
        from lib.messenger.recovery_message import RecoveryMessenger
        from lib.messenger.stamina_messenger import StaminaMessenger
        from lib.messenger.three_player_messenger import ThreePlayerMessenger
        from lib.messenger.two_player_messenger import TwoPlayerMessenger

        messenger_classes: dict[Messenger.Types, type['Messenger']] = {
            Messenger.Types.BALL: BallMessenger,
            Messenger.Types.PASS: PassMessenger,
            Messenger.Types.BALL_PLAYER: BallPlayerMessenger,
            Messenger.Types.BALL_GOALIE: BallGoalieMessenger,
            Messenger.Types.GOALIE_PLAYER: GoaliePlayerMessenger,
            Messenger.Types.GOALIE: GoalieMessenger,
            Messenger.Types.THREE_PLAYER: ThreePlayerMessenger,
            Messenger.Types.TWO_PLAYER: TwoPlayerMessenger,
            Messenger.Types.ONE_PLAYER: OnePlayerMessenger,
            Messenger.Types.RECOVERY: RecoveryMessenger,
            Messenger.Types.STAMINA: StaminaMessenger,
        }

        index = 0
        log.os_log().debug('*'*100)
        log.os_log().debug(sender)
        log.os_log().debug(messages)
        while index < len(messages):
            message_type = Messenger.Types(messages[index])
            message_size = Messenger.SIZES[message_type]

            message = messages[index+1: index+message_size]
            log.os_log().debug(messages[index: index + message_size])

            messenger_classes[message_type](message=message).decode(messenger_memory, sender, current_time)
            index += message_size




