from lib.messenger.converters import MessengerConverter
from lib.messenger.messenger import Messenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam


class StaminaMessenger(Messenger):
    CONVERTER = MessengerConverter([
        (0, 1, 74)
    ])

    def __init__(self,
                 stamina: float = None,
                 message: str = None):
        super().__init__()
        self._stamina: float = stamina

        self._size = Messenger.SIZES[Messenger.Types.STAMINA]
        self._header = Messenger.Types.STAMINA.value

        self._message = message

    def encode(self) -> str:
        SP = ServerParam.i()
        rate = (self._recovery - SP.recover_min()) / (SP.recover_init() - SP.recover_min())
        msg = StaminaMessenger.CONVERTER.convert_to_word([rate])
        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        rate = StaminaMessenger.CONVERTER.convert_to_values(self._message)

        messenger_memory.add_stamina(sender, rate, current_time)  # TODO IMP FUNC

    def __repr__(self):
        return 'recovery message'
