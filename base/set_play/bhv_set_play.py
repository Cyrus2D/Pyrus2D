from base.strategy import Strategy
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.player.object_player import PlayerObject
from lib.player.player_agent import PlayerAgent
from lib.rcsc.server_param import ServerParam


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
            if wm.ball().pos().x() < ServerParam.i().penalty_area_half_width() + 1 and \
                    wm.ball().pos().absY() < ServerParam.i().penalty_area_half_width() + 1:
                # return Bhv_SetPlayIndirectFreeKick().execute(agent)
                pass
            elif wm.ball().pos().x() > ServerParam.i().their_penalty_area_line_x() - 1 and \
                    wm.ball().pos().y() < ServerParam.i().penalty_area_half_width() + 1:
                # return Bhv_SetPlayIndirectFreeKick().execute(agent)
                pass

        if wm.game_mode().is_our_set_play(wm.our_side()):
            dlog.add_text(Level.TEAM, "SET PLAY our set play")
            # return Bhv_SetPlayFreeKick().execute(agent)
        else:
            # doBasicTheirSetPlayMove(agent)
            return True
        return False

    @staticmethod
    def is_kicker(agent: PlayerAgent):
        wm = agent.world()
        if wm.game_mode().mode_name() == "goalie_catch" and \
                wm.game_mode().side() == wm.our_side() and \
                not wm.self().goalie():
            dlog.add_text(Level.TEAM, "(is_kicker) goalie free kick")
            return False
        if not wm.self().goalie() and \
                wm.game_mode().mode_name() == "goal_kick" and \
                wm.game_mode().side() == wm.our_side():
            return False
        if wm.self().goalie() and \
                wm.game_mode().mode_name() == "goal_kick" and \
                wm.game_mode().side() == wm.our_side():
            return True
        st = Strategy()  # TODO Instance?!!?
        kicker_unum = 0
        min_dist2 = 1000000
        second_kicker_unum = 0
        second_min_dist2 = 1000000
        for unum in range(1, 12):
            if unum == wm.our_goalie_unum():
                continue

            home_pos = st.get_pos(unum)
            if not home_pos.is_valid():
                continue

            d2 = home_pos.dist2(wm.ball().pos())
            if d2 < second_min_dist2:
                second_kicker_unum = unum
                second_min_dist2 = d2

                if second_min_dist2 < min_dist2:
                    # swaping (fun in python :))
                    second_min_dist2, min_dist2 = min_dist2, second_min_dist2
                    second_kicker_unum, kicker_unum = kicker_unum, second_kicker_unum

        dlog.add_text(Level.TEAM, f"(is kicker) kicker_unum={kicker_unum}, second_kicker_unum={second_kicker_unum}")

        kicker: PlayerObject = None
        second_kicker: PlayerObject = None

        if kicker_unum != 0:
            kicker = wm.our_player(kicker_unum)
        if second_kicker_unum != 0:
            second_kicker = wm.our_player(second_kicker_unum)

        if kicker is None:
            if len(wm.teammates_from_ball()) > 0 and \
                    wm.teammates_from_ball()[0].dist_from_ball() < wm.ball().dist_from_self() * 0.9:
                dlog.add_text(Level.TEAM, "(is kicker) first kicker")
                return False

            dlog.add_text(Level.TEAM, "(is_kicker) self(1)")
            return True

        if kicker is not None and \
                second_kicker is not None and \
                (kicker.unum() == wm.self().unum() or \
                 second_kicker.unum() == wm.self().unum()):
            if min_dist2 ** 0.5 < (second_min_dist2 ** 0.5) * 0.95:
                dlog.add_text(Level.TEAM, f"(is kicker) kicker->unum={kicker.unum()} (1)")
                return kicker.unum() == wm.self().unum()
            elif kicker.dist_from_ball() < second_kicker.dist_from_ball() * 0.95:
                dlog.add_text(Level.TEAM, f"(is kicker) kicker->unum={kicker.unum()} (2)")
                return kicker.unum() == wm.self().unum()
            elif second_kicker.dist_from_ball() < kicker.dist_from_ball() * 0.95:
                dlog.add_text(Level.TEAM, f"(is kicker) kicker->unum={kicker.unum()} (3)")
                return second_kicker.unum() == wm.self().unum()
            elif len(wm.teammates_from_ball()) > 0 and \
                    wm.teammates_from_ball()[0].dist_from_ball() < wm.self().dist_from_ball() * 0.95:
                dlog.add_text(Level.TEAM, "(is kicker) other kicker")
                return False
            else:
                dlog.add_text(Level.TEAM, "(is kicker) self (2)")
                return True
        return kicker.unum() == wm.self().unum()
