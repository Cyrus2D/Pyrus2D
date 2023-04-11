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


class GoaliePlayerMessenger(Messenger):
    CONVERTER = MessengerConverter(Messenger.SIZES[Messenger.Types.GOALIE_PLAYER], [
        (53. - 16., 53., 160),
        (-20., 20., 400),
        (0, 360, 360),
        (1, 23, 22),
        (-ServerParam.i().pitch_half_length(), ServerParam.i().pitch_half_length(), 190),
        (-ServerParam.i().pitch_half_width(), ServerParam.i().pitch_half_width(), 124),
    ])

    def __init__(self,
                 goalie_unum: int = None,
                 goalie_pos: Vector2D = None,
                 goalie_body: AngleDeg = None,
                 player_unum: int = None,
                 player_pos: Vector2D = None,
                 message: str = None) -> None:
        super().__init__()
        if message is None:
            self._goalie_unum: int = goalie_unum
            self._goalie_pos: Vector2D = goalie_pos.copy()
            self._goalie_body: AngleDeg = goalie_body.copy()
            self._player_unum: int = player_unum
            self._player_pos: Vector2D = player_pos.copy()
        else:
            self._goalie_unum: int = None
            self._goalie_pos: Vector2D = None
            self._goalie_body: AngleDeg = None
            self._player_unum: int = None
            self._player_pos: Vector2D = None

        self._size = Messenger.SIZES[Messenger.Types.GOALIE_PLAYER]
        self._header = Messenger.Types.GOALIE_PLAYER.value

        self._message = message

    def encode(self) -> str:
        if self._goalie_pos.x() < 53. - 16 or self._goalie_pos.x() > 53 or self._goalie_pos.abs_y() > 20:
            log.sw_log().communication().add_text(f'(goalie player messenger) goalie pos over poisition range'
                                                  f': {self._goalie_pos}')
            return ''

        if not (1<=self._player_unum<=22):
            log.sw_log().communication().add_text(f'(goalie player messenger) player unum invalid'
                                                  f': {self._player_unum}')
            return ''

        SP = ServerParam.i()
        ep = 0.001
        msg = GoaliePlayerMessenger.CONVERTER.convert_to_word([
            bound(-SP.pitch_half_length() + ep, self._goalie_pos.x(), SP.pitch_half_length() - ep),
            bound(-SP.pitch_half_width() + ep, self._goalie_pos.y(), SP.pitch_half_width() - ep),
            bound(ep, self._goalie_body.degree() + 180, 360-ep),
            self._player_unum,
            bound(-SP.pitch_half_length() + ep, self._player_pos.x(), SP.pitch_half_length() - ep),
            bound(-SP.pitch_half_width() + ep, self._player_pos.y(), SP.pitch_half_width() - ep),
        ])
        return f'{self._header}{msg}'

    def decode(self, messenger_memory: MessengerMemory, sender: int, current_time: GameTime) -> None:
        gpx, gpy, gb, pu, ppx, ppy = GoaliePlayerMessenger.CONVERTER.convert_to_values(self._message)

        messenger_memory.add_opponent_goalie(sender, Vector2D(gpx, gpy), current_time, body=AngleDeg(gb-180))  # TODO IMP FUNC
        messenger_memory.add_player(sender,pu, Vector2D(ppx, ppy), current_time)  # TODO IMP FUNC

    def __repr__(self) -> str:
        return "ball player msg"
