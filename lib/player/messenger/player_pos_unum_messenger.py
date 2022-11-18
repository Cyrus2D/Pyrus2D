from lib.debug.level import Level
from lib.math.soccer_math import min_max
from lib.math.vector_2d import Vector2D
from lib.player.messenger.messenger import Messenger
from lib.rcsc.server_param import ServerParam
from lib.debug.logger import dlog

import lib.player.messenger.converters as converters

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.player.world_model import WorldModel

class PlayerPosUnumMessenger(Messenger):
    def __init__(self, unum: int = None, message:str=None) -> None:
        super().__init__()
        self._size = Messenger.SIZES[Messenger.Types.PLAYER_POS_VEL_UNUM]
        self._header = 'P'
        
        if message:
            self._pos: Vector2D = None
            self._unum: int = None
            self._message = message
        else:
            self._unum: int = unum
    
    def encode(self, wm: 'WorldModel') -> str:
        if not 1 <= self._unum <= 22:
            print(f"(player pos unum messenger encode) unum is out of limit. unum={self._unum}")
            return ""

        unum = self._unum % 11
        player = wm.our_player(unum) if self._unum // 11 == 0 else wm.their_player(unum)
        
        if player is None:
            print(f"(player pos unum messenger encode) player is None. unum={self._unum}")
        
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
    
    def decode(self, wm: 'WorldModel', sender: int) -> None:
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
        
        dlog.add_text(Level.SENSOR, f"(PlayerPosUnumMessenger decode) receive a player. unum={unum}, pos={pos}")

        wm.update_player_by_hear(Messenger.Player(sender, unum, pos))
    
        