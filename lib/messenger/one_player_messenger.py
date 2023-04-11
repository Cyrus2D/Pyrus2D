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


class OnePlayerMessenger(Messenger):
    CONVERTER = MessengerConverter(Messenger.SIZES[Messenger.Types.ONE_PLAYER], [
        (1, 23, 22),
        (-ServerParam.i().pitch_half_length(), ServerParam.i().pitch_half_length(), 168),
        (-ServerParam.i().pitch_half_width(), ServerParam.i().pitch_half_width(), 108),
    ])

    def __init__(self,
                 u1: int = None,
                 p1: Vector2D = None,
                 message: str = None) -> None:
        super().__init__()
        if message is None:
            self._unums: list[int] = [u1]
            self._player_poses: list[Vector2D] = [p1.copy()]
        else:
            self._unums: list[int] = None
            self._player_poses: list[Vector2D] = None

        self._size = Messenger.SIZES[Messenger.Types.ONE_PLAYER]
        self._header = Messenger.Types.ONE_PLAYER.value

        self._message = message

    def encode(self) -> str:
        data = []
        SP = ServerParam.i()
        ep = 0.001
        for p, u in zip(self._player_poses, self._unums):
            if not 1 <= u <= 22:
                log.os_log().error(f'(ball player messenger) illegal unum={u}')
                log.sw_log().sensor().add_text(f'(ball player messenger) illegal unum={u}')
                return ''
            data.append(u)
            data.append(bound(-SP.pitch_half_length() + ep, p.x(), SP.pitch_half_length() - ep))
            data.append(bound(-SP.pitch_half_width() + ep, p.y(), SP.pitch_half_width() - ep))

        msg = OnePlayerMessenger.CONVERTER.convert_to_word(data)
        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        data = OnePlayerMessenger.CONVERTER.convert_to_values(self._message)
        for i in range(1):
            u = data[i * 3]
            px = data[i * 3 + 1]
            py = data[i * 3 + 2]

            messenger_memory.add_player(sender,u,  Vector2D(px, py), current_time)  # TODO IMP FUNC

    def __repr__(self) -> str:
        return "ball player msg"
