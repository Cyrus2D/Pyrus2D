import team_config
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import UNUM_UNKNOWN, GameModeType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class SampleCommunication:
    def __init__(self):
        self._current_sender_unum: int = UNUM_UNKNOWN
        self._next_sender_unum: int = UNUM_UNKNOWN
        self._ball_send_time: GameTime = GameTime(0, 0)
        self._teammate_send_time: list[GameTime] = [GameTime(0, 0) for i in range(12)]
        self._opponent_send_time: list[GameTime] = [GameTime(0, 0) for i in range(12)]

    def execute(self, agent: 'PlayerAgent'):
        if not team_config.USE_COMMUNICATION:  # TODO IMP FUNC
            return False

        self.update_current_sender(agent)  # TODO IMP FUNC

        wm = agent.world()
        penalty_shootout = wm.game_mode().is_penalty_kick_mode()

        say_recovery = False
        if wm.game_mode().type() == GameModeType.PlayOn \
                and not penalty_shootout \
                and self._current_sender_unum == wm.self().unum() \
                and wm.self().recovery() < ServerParam.i().recover_init() - 0.002:
            say_recovery = True
            self.say_recovery(agent)  # TODO IMP FUNC

        if wm.game_mode().type() == GameModeType.BeforeKickOff \
                or wm.game_mode().type().is_after_goal() \
                or penalty_shootout:
            return say_recovery

        self.say_ball_and_players(agent)  # TODO IMP FUNC
        self.say_stamina(agent)  # TODO IMP FUNC

        self.attention_to_someone(agent)  # TODO IMP FUNC

        return True
