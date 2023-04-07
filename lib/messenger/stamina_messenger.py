from lib.messenger.converters import MessengerConverter
from lib.messenger.messenger import Messenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam


class StaminaMessenger(Messenger):
    CONVERTER = MessengerConverter(Messenger.SIZES[Messenger.Types.STAMINA], [
        (0, ServerParam.i().stamina_max()+1, 74)
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
        msg = StaminaMessenger.CONVERTER.convert_to_word([self._stamina])
        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        rate = StaminaMessenger.CONVERTER.convert_to_values(self._message)[0]

        messenger_memory.add_stamina(sender, rate, current_time)

    def __repr__(self):
        return 'recovery message'
