from lib.action.go_to_point import *
from base.strategy import *
from lib.debug.logger import *
from base.set_play.bhv_set_play import Bhv_SetPlay
from base.bhv_kick import BhvKick
from base.bhv_move import BhvMove


def get_decision(agent):
    st = Strategy()
    wm: WorldModel = agent.world()

    if wm.game_mode().type() != GameModeType.PlayOn:
        return Bhv_SetPlay().execute(agent)
    if wm.self().is_kickable():
        return BhvKick().execute(agent)
    return BhvMove().execute(agent)
