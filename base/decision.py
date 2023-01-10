from base.strategy_formation import StrategyFormation
from base.set_play.bhv_set_play import Bhv_SetPlay
from base.bhv_kick import BhvKick
from base.bhv_move import BhvMove
from lib.action.neck_scan_field import NeckScanField
from lib.action.neck_scan_players import NeckScanPlayers
from lib.action.neck_turn_to_ball import NeckTurnToBall
from lib.action.neck_turn_to_ball_or_scan import NeckTurnToBallOrScan
from lib.debug.debug_print import debug_print
from lib.messenger.ball_pos_vel_messenger import BallPosVelMessenger
from lib.messenger.player_pos_unum_messenger import PlayerPosUnumMessenger
from lib.rcsc.types import GameModeType, ViewWidth

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.player_agent import PlayerAgent

# TODO VIEW TACTICAL
# TODO CHECK ORDER
# TODO CALL NECK ACTION AFTER MAIN ACTIONS

# TODO do preprocess
# TODO DLOG ON SCCORWINDOW
def get_decision(agent: 'PlayerAgent'):
    wm: 'WorldModel' = agent.world()
    st = StrategyFormation().i()
    st.update(wm)
    
    # agent.do_change_view(ViewWidth.WIDE)
    NeckTurnToBallOrScan(5).execute(agent)
    
    if wm.self().unum() == 5: # TODO REMOVE IT
        agent.add_say_message(BallPosVelMessenger())
        agent.add_say_message(PlayerPosUnumMessenger(9))
    else:
        agent.do_attentionto(wm.our_side(), 5)

    if wm.game_mode().type() != GameModeType.PlayOn:
        return Bhv_SetPlay().execute(agent)
    if wm.self().is_kickable():
        return BhvKick().execute(agent)
    return BhvMove().execute(agent)
