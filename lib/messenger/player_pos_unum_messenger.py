from lib.debug.debug import log
from lib.debug.level import Level
from pyrusgeom.soccer_math import min_max
from pyrusgeom.vector_2d import Vector2D
from lib.messenger.messenger import Messenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam

import lib.messenger.converters as converters

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.player.world_model import WorldModel

class PlayerPosUnumMessenger(Messenger):
    def __init__(self, unum: int = None, message:str=None) -> None:
        super().__init__()
        self._size = Messenger.SIZES[Messenger.Types.PLAYER_POS_VEL_UNUM]
        self._header = Messenger.Types.PLAYER_POS_VEL_UNUM.value
        
        if message:
            self._unum: int = None
            self._message = message
        else:
            self._unum: int = unum
            self._message = None
    
    def encode(self) -> str:
        if not 1 <= self._unum <= 22:
            log.os_log().error(f"(player pos unum messenger encode) unum is out of limit. unum={self._unum}")
            return ""

        unum = self._unum % 11
        player = wm.our_player(unum) if self._unum // 11 == 0 else wm.their_player(unum)
        
        if player is None:
            log.os_log().error(f"(player pos unum messenger encode) player is None. unum={self._unum}")
            return None
        
        SP = ServerParam.i()
        
        pos = player.pos()
        x:float = min_max(-SP.pitch_half_length(), pos.x(), SP.pitch_half_length()) + SP.pitch_half_length()
        y:float = min_max(-SP.pitch_half_width(), pos.y(), SP.pitch_half_width()) + SP.pitch_half_width()

        val = self._unum - 1
        
        val *= 168
        val += int(x/0.63)

        val *= 109
        val += int(y/0.63)

        return self._header + converters.convert_to_words(val, self._size - 1)
    
    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        SP = ServerParam.i()

        val = converters.convert_to_int(self._message[1:])
        if val is None:
            return
        
        y  = (val % 109)*0.63 - SP.pitch_half_width()
        val = int(val/109)
        
        x = (val % 168)*0.63 - SP.pitch_half_length()
        val = int(val/168)

        unum = (val%22) + 1
        pos = Vector2D(x,y)
        
        log.sw_log().sensor().add_text( f"(PlayerPosUnumMessenger decode) receive a player. unum={unum}, pos={pos}")

        messenger_memory.add_player(sender, unum, pos, current_time)
    
    def __repr__(self) -> str:
        return "player pos unum msg"
        