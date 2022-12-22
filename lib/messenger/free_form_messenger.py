from lib.messenger.messenger import Messenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.rcsc.game_time import GameTime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.coach.gloabl_world_model import GlobalWorldModel

class FreeFormMessenger(Messenger):
    def __init__(self) -> None:
        super().__init__()
    
    def encode(self, wm: 'GlobalWorldModel') -> str:
        return super().encode(wm)
    
    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        return super().decode(messenger_memory, sender, current_time)