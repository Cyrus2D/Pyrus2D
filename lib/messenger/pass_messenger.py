from pyrusgeom.soccer_math import min_max, bound
from pyrusgeom.vector_2d import Vector2D

from lib.messenger.converters import MessengerConverter
from lib.messenger.messenger import Messenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam

import lib.messenger.converters as converters

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.player.world_model import WorldModel


class PassMessenger(Messenger):
    CONVERTER = MessengerConverter(Messenger.SIZES[Messenger.Types.PASS], [
        (-ServerParam.i().pitch_half_length(), ServerParam.i().pitch_half_length(), 2 ** 10),
        (-ServerParam.i().pitch_half_width(), ServerParam.i().pitch_half_width(), 2 ** 9),
        (1, 12, 11),
        (-ServerParam.i().pitch_half_length(), ServerParam.i().pitch_half_length(), 2 ** 10),
        (-ServerParam.i().pitch_half_width(), ServerParam.i().pitch_half_width(), 2 ** 9),
        (-ServerParam.i().ball_speed_max(), ServerParam.i().ball_speed_max(), 2 ** 6),
        (-ServerParam.i().ball_speed_max(), ServerParam.i().ball_speed_max(), 2 ** 6),
    ])
    def __init__(self,
                 receiver_unum: int = None,
                 receive_point: Vector2D = None,
                 ball_pos: Vector2D = None,
                 ball_vel: Vector2D = None,
                 message: str = None) -> None:
        super().__init__()
        self._size = Messenger.SIZES[Messenger.Types.PASS]
        self._header = Messenger.Types.PASS.value

        if message:
            self._message = message
            return
        self._receiver_unum = receiver_unum
        self._receive_point = receive_point.copy()
        self._ball_pos = ball_pos.copy()
        self._ball_vel = ball_vel.copy()

    def encode(self) -> str:
        SP = ServerParam.i()
        ep = 0.001
        msg = PassMessenger.CONVERTER.convert_to_word([
            bound(-SP.pitch_half_length() + ep, self._receive_point.x(), SP.pitch_half_length() - ep),
            bound(-SP.pitch_half_width() + ep, self._receive_point.y(), SP.pitch_half_width() - ep),
            self._receiver_unum,
            bound(-SP.pitch_half_length() + ep, self._ball_pos.x(), SP.pitch_half_length() - ep),
            bound(-SP.pitch_half_width() + ep, self._ball_pos.y(), SP.pitch_half_width() - ep),
            bound(ep, self._ball_vel.x(), SP.ball_speed_max() - ep),
            bound(ep, self._ball_vel.y(), SP.ball_speed_max() - ep),
        ])

        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        rpx, rpy, ru, bpx, bpy, bvx, bvy = PassMessenger.CONVERTER.convert_to_values(self._message)

        messenger_memory.add_pass(sender, ru, Vector2D(rpx, rpy), current_time)
        messenger_memory.add_ball(sender, Vector2D(bpx, bpy), Vector2D(bvx, bvy), current_time)

    def __repr__(self) -> str:
        return "ball pos vel msg"

