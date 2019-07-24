from lib.action.go_to_point import *
from base.strategy import *
from lib.debug.logger import *
from base.set_play import SetPlay
from base.bhv_kick import BhvKick
from base.bhv_move import BhvMove

# TIP: 
# game mode use:
# if agent.world().game_mode() ==  PlayMode.PlayOn:
#     pass
# or
# if agent.world().game_mode().value == "play_on":
#     pass


def get_decision(agent):
    st = Strategy()
    wm: WorldModel = agent.world()

    if wm.game_mode() is not 'play_on ':
        return SetPlay().execute(agent)
    if wm.self().isKickable():
        return BhvKick().execute(agent)
    return BhvMove().execute(agent)
