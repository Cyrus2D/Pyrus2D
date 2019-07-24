from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.player.player_agent import PlayerAgent
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import PlayMode


class Bhv_SetPlay:
    def __init__(self):
        # nothing to say :)
        pass

    def execute(self, agent: PlayerAgent):
        dlog.add_text(Level.TEAM, "Bhv_SetPlay")
        wm = agent.world()
        mode_name = wm.game_mode().mode_name()
        game_side = wm.game_mode().side()

        if wm.self().goalie():  # and not startegy.isgoalforward
            if mode_name == "goal_kick":
                if game_side == wm.our_side():
                    # return Bhv_SetPlayGoalKick().execute(agent)
                    pass
            if mode_name != "back_pass" and mode_name != "indirect_free_kick":
                # Bhv_GoalieFreeKick().execute(agnet)
                pass
            else:
                # Bhv_SetPlayIndirectFreeKick().execute(agent)
                pass

            return True

        if mode_name == "kick_off":
            if game_side == wm.our_side():
                # return Bhv_SetPlayKickOff().execute(agent)
                pass
            else:
                # doBasicTheirSetPlayMove(agent)
                return True
        elif mode_name == "kick_in" or mode_name == "corner_kick":
            if game_side == wm.our_side():
                # return Bhv_SetPlayKickIn().execute(agent)
                pass
            else:
                # doBasicTheirSetPlayMove(agent)
                return True
        elif mode_name == "goal_kick":
            if game_side == wm.our_side():
                # return Bhv_SetPlayGoalKick().execute(agent)
                pass
            else:
                # return Bhv_TheirGoalKickMove().execute(agent)
                pass
        elif mode_name == "back_pass" or mode_name == "indirect_free_kick":
            # return Bhv_SetPlayIndirectFreeKick().execute(agent)
            pass
        elif mode_name == "foul_charge" or mode_name == "foul_push":
            if wm.ball().pos().x() < ServerParam.i().penalty_area_half_width() + 1 and wm.ball().pos().absY() < ServerParam.i().penalty_area_half_width() + 1:
                # return Bhv_SetPlayIndirectFreeKick().execute(agent)
                pass
            elif wm.ball().pos().x() > ServerParam.i().their_penalty_area_line_x() - 1 and wm.ball().pos().y() < ServerParam.i().penalty_area_half_width() + 1:
                # return Bhv_SetPlayIndirectFreeKick().execute(agent)
                pass

        if wm.game_mode().is_our_set_play(wm.our_side()):
            dlog.add_text(Level.TEAM, "SET PLAY our set play")
            # return Bhv_SetPlayFreeKick().execute(agent)
        else:
            # doBasicTheirSetPlayMove(agent)
            return True
        return False
