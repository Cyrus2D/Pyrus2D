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


class GoalieMessenger(Messenger):
    CONVERTER = MessengerConverter([
        (53. - 16., 53., 160),
        (-20., 20., 400),
        (0, 360, 360),
    ])

    def __init__(self,
                 goalie_unum: int = None,
                 goalie_pos: Vector2D = None,
                 goalie_body: AngleDeg = None,
                 message: str = None) -> None:
        super().__init__()
        self._goalie_unum: int = goalie_unum
        self._goalie_pos: Vector2D = goalie_pos.copy()
        self._goalie_body: AngleDeg = goalie_body.copy()

        self._size = Messenger.SIZES[Messenger.Types.GOALIE]
        self._header = Messenger.Types.GOALIE.value

        self._message = message

    def encode(self, wm: 'WorldModel') -> str:
        if self._goalie_pos.x() < 53. - 16 or self._goalie_pos.x() > 53 or self._goalie_pos.abs_y() > 20:
            log.sw_log().communication().add_text(f'(goalie player messenger) goalie pos over poisition range'
                                                  f': {self._goalie_pos}')
            return ''

        msg = GoalieMessenger.CONVERTER.convert_to_word([
            self._goalie_pos.x(),
            self._goalie_pos.y(),
            self._goalie_body.degree() + 180,
        ])
        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        gpx, gpy, gb = GoalieMessenger.CONVERTER.convert_to_values(self._message)

        messenger_memory.add_opponent_goalie(sender, Vector2D(gpx, gpy), current_time, body=AngleDeg(gb))  # TODO IMP FUNC

    def __repr__(self) -> str:
        return "ball player msg"
