from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.vector_2d import Vector2D

from lib.debug.debug import log
from lib.messenger.converters import MessengerConverter
from lib.messenger.messenger import Messenger

from lib.messenger.messenger_memory import MessengerMemory
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel


class BallMessenger(Messenger):
    CONVERTER = MessengerConverter([
        (-ServerParam.i().pitch_half_length(), ServerParam.i().pitch_half_length(), 2 ** 10),
        (-ServerParam.i().pitch_half_width(), ServerParam.i().pitch_half_width(), 2 ** 9),
        (-ServerParam.i().ball_speed_max(), ServerParam.i().ball_speed_max(), 2 ** 6),
        (-ServerParam.i().ball_speed_max(), ServerParam.i().ball_speed_max(), 2 ** 6),
    ])

    def __init__(self,
                 ball_pos: Vector2D = None,
                 ball_vel: Vector2D = None,
                 message: str = None) -> None:
        super().__init__()
        self._ball_pos: Vector2D = ball_pos.copy()
        self._ball_vel: Vector2D = ball_vel.copy()

        self._size = Messenger.SIZES[Messenger.Types.BALL]
        self._header = Messenger.Types.BALL.value
        self._message = message

    def encode(self, wm: 'WorldModel') -> str:
        msg = BallMessenger.CONVERTER.convert_to_word([
            self._ball_pos.x(),
            self._ball_pos.y(),
            self._ball_vel.x(),
            self._ball_vel.y(),
        ])
        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        bpx, bpy, bvx, bvy = BallMessenger.CONVERTER.convert_to_values(self._message)

        messenger_memory.add_ball(sender, Vector2D(bpx, bpy), Vector2D(bvx, bvy), current_time)

    def __repr__(self) -> str:
        return "ball msg"
