from base import goalie_decision
from base.strategy_formation import StrategyFormation
from base.set_play.bhv_set_play import Bhv_SetPlay
from base.bhv_kick import BhvKick
from base.bhv_move import BhvMove
from lib.action.neck_scan_field import NeckScanField
from lib.action.neck_scan_players import NeckScanPlayers
from lib.action.neck_turn_to_ball import NeckTurnToBall
from lib.action.neck_turn_to_ball_or_scan import NeckTurnToBallOrScan
from lib.action.scan_field import ScanField
from lib.debug.debug import log
from lib.messenger.ball_pos_vel_messenger import BallPosVelMessenger
from lib.messenger.player_pos_unum_messenger import PlayerPosUnumMessenger
from lib.rcsc.types import GameModeType, ViewWidth, UNUM_UNKNOWN

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.player_agent import PlayerAgent


# TODO TACKLE GEN
# TODO GOAL KICK L/R
# TODO GOAL L/R
def get_decision(agent: 'PlayerAgent'):
    wm: 'WorldModel' = agent.world()
    st = StrategyFormation().i()
    st.update(wm)

    if wm.self().goalie:
        if goalie_decision.decision(agent):
            return True

    if wm.game_mode().type() != GameModeType.PlayOn:
        if Bhv_SetPlay().execute(agent):
            return True

    log.sw_log().team().add_text(f'is kickable? dist {wm.ball().dist_from_self} '
                                 f'ka {wm.self().player_type.kickable_area()} '
                                 f'seen pos count {wm.ball().seen_pos_count} '
                                 f'is? {wm.self().is_kickable()}')
    if wm.self().is_kickable():
        return BhvKick().execute(agent)
    if BhvMove().execute(agent):
        return True
    log.os_log().warn("NO ACTION, ScanFIELD")
    return ScanField().execute(agent)