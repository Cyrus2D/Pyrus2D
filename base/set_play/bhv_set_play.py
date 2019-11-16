from base.set_play.bhv_set_play_before_kick_off import Bhv_BeforeKickOff
from base.strategy_formation import *
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.action.go_to_point import *


class Bhv_SetPlay:
    def __init__(self):
        # nothing to say :)
        pass

    def execute(self, agent):
        dlog.add_text(Level.TEAM, "Bhv_SetPlay")
        wm: WorldModel = agent.world()
        game_mode = wm.game_mode().type()
        game_side = wm.game_mode().side()

        if game_mode is GameModeType.BeforeKickOff:
            return Bhv_BeforeKickOff().execute(agent)

        st = StrategyFormation.i()
        target = st.get_pos(wm.self().unum())
        if wm.game_mode().side() is wm.our_side():
            nearest_tm_dist = 1000
            nearest_tm = 0
            for i in range(1, 12):
                tm: PlayerObject = wm.our_player(i)
                if tm.unum() is i:
                    dist = tm.pos().dist(wm.ball().pos())
                    if dist < nearest_tm_dist:
                        nearest_tm_dist = dist
                        nearest_tm = i
            if nearest_tm is wm.self().unum():
                target = wm.ball().pos()
        GoToPoint(target, 0.5, 100).execute(agent)

    @staticmethod
    def is_kicker(agent):
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
        st = StrategyFormation().i()  # TODO Instance?!!?
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
