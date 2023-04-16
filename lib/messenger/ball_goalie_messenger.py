from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.soccer_math import bound
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


class BallGoalieMessenger(Messenger):
    CONVERTER = MessengerConverter(Messenger.SIZES[Messenger.Types.BALL_GOALIE], [
        (-ServerParam.i().pitch_half_length(), ServerParam.i().pitch_half_length(), 2 ** 10),
        (-ServerParam.i().pitch_half_width(), ServerParam.i().pitch_half_width(), 2 ** 9),
        (-ServerParam.i().ball_speed_max(), ServerParam.i().ball_speed_max(), 2 ** 6),
        (-ServerParam.i().ball_speed_max(), ServerParam.i().ball_speed_max(), 2 ** 6),
        (-ServerParam.i().pitch_half_length(), ServerParam.i().pitch_half_length(), 106),
        (-ServerParam.i().pitch_half_width(), ServerParam.i().pitch_half_width(), 69),
        (0, 360, 180)
    ])

    def __init__(self,
                 ball_pos: Vector2D = None,
                 ball_vel: Vector2D = None,
                 player_pos: Vector2D = None,
                 player_body: AngleDeg = None,
                 message: str = None) -> None:
        super().__init__()
        if message is None:
            self._ball_pos: Vector2D = ball_pos.copy()
            self._ball_vel: Vector2D = ball_vel.copy()
            self._player_pos: Vector2D = player_pos.copy()
            self._player_body: AngleDeg = player_body.copy()
        else:
            self._ball_pos: Vector2D = None
            self._ball_vel: Vector2D = None
            self._player_pos: Vector2D = None
            self._player_body: AngleDeg = None
        self._size = Messenger.SIZES[Messenger.Types.BALL_GOALIE]
        self._header = Messenger.Types.BALL_GOALIE.value

        self._message = message

    def encode(self) -> str:
        if self._ball_pos.abs_x() > ServerParam.i().pitch_half_length() \
                or self._ball_pos.abs_y() > ServerParam.i().pitch_half_width():
            return ''

        SP = ServerParam.i()
        ep = 0.001
        msg = BallGoalieMessenger.CONVERTER.convert_to_word([
            bound(-SP.pitch_half_length() + ep, self._ball_pos.x(), SP.pitch_half_length() - ep),
            bound(-SP.pitch_half_width() + ep, self._ball_pos.y(), SP.pitch_half_width() - ep),
            bound(-SP.ball_speed_max() + ep, self._ball_vel.x(), SP.ball_speed_max() - ep),
            bound(-SP.ball_speed_max() + ep, self._ball_vel.y(), SP.ball_speed_max() - ep),
            bound(-SP.pitch_half_length() + ep, self._player_pos.x(), SP.pitch_half_length() - ep),
            bound(-SP.pitch_half_width() + ep, self._player_pos.y(), SP.pitch_half_width() - ep),
            bound(ep, self._player_body.degree() + 180, 360. - ep)
        ])
        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        bpx, bpy, bvx, bvy, ppx, ppy, pb = BallGoalieMessenger.CONVERTER.convert_to_values(self._message)

        messenger_memory.add_ball(sender, Vector2D(bpx, bpy), Vector2D(bvx, bvy), current_time)
        messenger_memory.add_opponent_goalie(sender, Vector2D(ppx, ppy), current_time, body=AngleDeg(pb-180))  # TODO IMP FUNC

    def __repr__(self) -> str:
        return "ball player msg"
