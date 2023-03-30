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

class BallPosVelMessenger(Messenger):
    def __init__(self, message:str=None) -> None:
        super().__init__()
        self._size = Messenger.SIZES[Messenger.Types.BALL_POS_VEL_MESSAGE]
        self._header = Messenger.Types.BALL_POS_VEL_MESSAGE.value
        
        self._message = message
    
    def encode(self) -> str:
        if not wm.ball().pos_valid():
            return
        if not wm.ball().vel_valid():
            return
        
        SP = ServerParam.i()
        pos = wm.ball().pos().copy()
        vel = wm.ball().vel().copy()
        
        x:float = min_max(-SP.pitch_half_length(), pos.x(), SP.pitch_half_length()) + SP.pitch_half_length()
        y:float = min_max(-SP.pitch_half_width(), pos.y(), SP.pitch_half_width()) + SP.pitch_half_width()
        
        x= int(x*1024/(SP.pitch_half_length()*2))
        y= int(y*512/(SP.pitch_half_width()*2))

        max_speed = SP.ball_speed_max()
        vx = min_max(-max_speed, vel.x(), max_speed) + max_speed
        vy = min_max(-max_speed, vel.y(), max_speed) + max_speed

        vx = int(vx*64/(max_speed*2))
        vy = int(vy*64/(max_speed*2))
        
        val = x
        val *= 2**9
        val += y
        
        val*=2**6
        val += vx
        val*=2**6
        val += vy
        
        return self._header + converters.convert_to_words(val, self._size - 1)
    
    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        SP = ServerParam.i()

        val = converters.convert_to_int(self._message[1:])
        if val is None:
            return
        
        vy = val% 64
        val = int(val/64)
        
        vx = val% 64
        val = int(val/64)
        
        y = val% 512
        val = int(val/512)

        x = val
        
        x = x / 1024 * SP.pitch_half_length()*2 - SP.pitch_half_length()
        y = y / 512 * SP.pitch_half_width()*2 - SP.pitch_half_width()

        vx = vx /64 *SP.ball_speed_max()*2 - SP.ball_speed_max()
        vy = vy /64 *SP.ball_speed_max()*2 - SP.ball_speed_max()
        
        pos = Vector2D(x, y)
        vel = Vector2D(vx, vy)
        
        messenger_memory.add_ball(sender, pos, vel, current_time)

    def __repr__(self) -> str:
        return "ball pos vel msg"

        