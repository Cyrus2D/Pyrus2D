from base.strategy_formation import StrategyFormation
from base.set_play.bhv_set_play import Bhv_SetPlay
from lib.player.templates import *
from base.bhv_kick import BhvKick
from base.bhv_move import BhvMove
from lib.debug.debug_print import debug_print


def get_decision(agent):
    debug_print("Decisioning...")
    wm: WorldModel = agent.world()
    st = StrategyFormation().i()
    st.update(wm)

    if wm.game_mode().type() != GameModeType.PlayOn:
        return Bhv_SetPlay().execute(agent)
    if wm.self().is_kickable():
        return BhvKick().execute(agent)
    return BhvMove().execute(agent)
