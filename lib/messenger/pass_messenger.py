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


class PassMessenger(Messenger):
    def __init__(self,
                 receiver_unum: int,
                 receive_point: Vector2D,
                 ball_pos: Vector2D,
                 ball_vel: Vector2D,
                 message: str = None) -> None:
        super().__init__()
        self._size = Messenger.SIZES[Messenger.Types.PASS]
        self._header = Messenger.Types.PASS.value

        self._receiver_unum = receiver_unum
        self._receive_point = receive_point.copy()
        self._ball_pos = ball_pos.copy()
        self._ball_vel = ball_vel.copy()

        self._message = message

    def encode(self, wm: 'WorldModel') -> str:
        if not wm.ball().pos_valid():
            return
        if not wm.ball().vel_valid():
            return

        SP = ServerParam.i()

        pos = self._receive_point
        x: float = min_max(-SP.pitch_half_length(), pos.x(), SP.pitch_half_length()) + SP.pitch_half_length()
        y: float = min_max(-SP.pitch_half_width(), pos.y(), SP.pitch_half_width()) + SP.pitch_half_width()

        x = int(x * 1024 / (SP.pitch_half_length() * 2))
        y = int(y * 512 / (SP.pitch_half_width() * 2))

        val = x
        val *= 2 ** 9
        val += y

        val *= 2**4
        val += self._receiver_unum

        pos = self._ball_pos
        vel = self._ball_vel

        x: float = min_max(-SP.pitch_half_length(), pos.x(), SP.pitch_half_length()) + SP.pitch_half_length()
        y: float = min_max(-SP.pitch_half_width(), pos.y(), SP.pitch_half_width()) + SP.pitch_half_width()

        x = int(x * 1024 / (SP.pitch_half_length() * 2))
        y = int(y * 512 / (SP.pitch_half_width() * 2))

        max_speed = SP.ball_speed_max()
        vx = min_max(-max_speed, vel.x(), max_speed) + max_speed
        vy = min_max(-max_speed, vel.y(), max_speed) + max_speed

        vx = int(vx * 64 / (max_speed * 2))
        vy = int(vy * 64 / (max_speed * 2))

        val *= 2**10
        val += x
        val *= 2 ** 9
        val += y

        val *= 2 ** 6
        val += vx
        val *= 2 ** 6
        val += vy

        return self._header + converters.convert_to_words(val, self._size - 1)

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        SP = ServerParam.i()

        val = converters.convert_to_int(self._message[1:])
        if val is None:
            return

        vy = val % 64
        val = val // 64

        vx = val % 64
        val = val // 64

        y = val % 512
        val = val // 512

        x = val % 1024
        val = val // 1024

        unum = val % 16
        val = val // 16

        ry = val % 512
        val = val // 512

        rx = val

        x = x / 1024 * SP.pitch_half_length() * 2 - SP.pitch_half_length()
        y = y / 512 * SP.pitch_half_width() * 2 - SP.pitch_half_width()

        rx = rx / 1024 * SP.pitch_half_length() * 2 - SP.pitch_half_length()
        ry = ry / 512 * SP.pitch_half_width() * 2 - SP.pitch_half_width()

        vx = vx / 64 * SP.ball_speed_max() * 2 - SP.ball_speed_max()
        vy = vy / 64 * SP.ball_speed_max() * 2 - SP.ball_speed_max()

        pos = Vector2D(x, y)
        vel = Vector2D(vx, vy)

        receiver_pos = Vector2D(rx, ry)

        messenger_memory.add_pass(sender, unum, receiver_pos, current_time)
        messenger_memory.add_ball(sender, pos, vel, current_time)

    def __repr__(self) -> str:
        return "ball pos vel msg"

