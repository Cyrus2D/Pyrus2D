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


class BallPlayerMessenger(Messenger):
    CONVERTER = MessengerConverter([
        (-ServerParam.i().pitch_half_length(), ServerParam.i().pitch_half_length(), 2 ** 10),
        (-ServerParam.i().pitch_half_width(), ServerParam.i().pitch_half_width(), 2 ** 9),
        (-ServerParam.i().ball_speed_max(), ServerParam.i().ball_speed_max(), 2 ** 6),
        (-ServerParam.i().ball_speed_max(), ServerParam.i().ball_speed_max(), 2 ** 6),
        (0, 23, 23),
        (-ServerParam.i().pitch_half_length(), ServerParam.i().pitch_half_length(), 106),
        (-ServerParam.i().pitch_half_width(), ServerParam.i().pitch_half_width(), 69),
        (0, 360, 180)
    ])

    def __init__(self,
                 ball_pos: Vector2D = None,
                 ball_vel: Vector2D = None,
                 unum: int = None,
                 player_pos: Vector2D = None,
                 player_body: AngleDeg = None,
                 message: str = None) -> None:
        super().__init__()
        self._ball_pos: Vector2D = ball_pos.copy()
        self._ball_vel: Vector2D = ball_vel.copy()
        self._unum: int = unum
        self._player_pos: Vector2D = player_pos.copy()
        self._player_body: AngleDeg = player_body.copy()
        self._size = Messenger.SIZES[Messenger.Types.BALL_PLAYER]
        self._header = Messenger.Types.BALL_PLAYER.value

        self._message = message

    def encode(self) -> str:
        if not 1 <= self._unum <= 22:
            log.os_log().error(f'(ball player messenger) illegal unum={self._unum}')
            log.sw_log().sensor().add_text(f'(ball player messenger) illegal unum={self._unum}')
            return ''

        msg = BallPlayerMessenger.CONVERTER.convert_to_word([
            self._ball_pos.x(),
            self._ball_pos.y(),
            self._ball_vel.x(),
            self._ball_vel.y(),
            self._unum,
            self._player_pos.x(),
            self._player_pos.y(),
            self._player_body.degree() + 180
        ])
        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        bpx, bpy, bvx, bvy, pu, ppx, ppy, pb = BallPlayerMessenger.CONVERTER.convert_to_values(self._message)

        messenger_memory.add_ball(sender, Vector2D(bpx, bpy), Vector2D(bvx, bvy), current_time)
        messenger_memory.add_player(sender, Vector2D(ppx, ppy), current_time, body=AngleDeg(pb-180))  # TODO IMP FUNC

    def __repr__(self) -> str:
        return "ball player msg"
