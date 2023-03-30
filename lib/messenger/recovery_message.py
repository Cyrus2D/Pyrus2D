from lib.messenger.converters import MessengerConverter
from lib.messenger.messenger import Messenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam


class RecoveryMessenger(Messenger):
    CONVERTER = MessengerConverter([
        (0, 1, 74)
    ])

    def __init__(self,
                 recovery: float = None,
                 message: str = None):
        super().__init__()
        self._recovery: float = recovery

        self._size = Messenger.SIZES[Messenger.Types.RECOVERY]
        self._header = Messenger.Types.RECOVERY.value

        self._message = message

    def encode(self) -> str:
        SP = ServerParam.i()
        rate = (self._recovery - SP.recover_min()) / (SP.recover_init() - SP.recover_min())
        msg = RecoveryMessenger.CONVERTER.convert_to_word([rate])
        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        rate = RecoveryMessenger.CONVERTER.convert_to_values(self._message)

        messenger_memory.add_recovery(sender, rate, current_time)  # TODO IMP FUNC

    def __repr__(self):
        return 'recovery message'
