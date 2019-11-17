from lib.action.go_to_point import *
from base.strategy_formation import *
from lib.action.intercept import Intercept
from lib.debug.logger import *
from lib.player.templates import *


class BhvMove:
    def __init__(self):
        pass

    def execute(self, agent: PlayerAgent):
        wm: WorldModel = agent.world()
        # intercept
        self_min = wm.intercept_table().self_reach_cycle()
        tm_min = wm.intercept_table().teammate_reach_cycle()
        opp_min = wm.intercept_table().opponent_reach_cycle()
        dlog.add_text(Level.BLOCK,
                      f"self_min={self_min}")
        dlog.add_text(Level.BLOCK,
                      f"tm_min={tm_min}")
        dlog.add_text(Level.BLOCK,
                      f"opp_min={opp_min}")

        if (not wm.exist_kickable_teammates()
                and (self_min <= 5
                     or (self_min <= tm_min
                         and self_min < opp_min + 5))):
            dlog.add_text(Level.BLOCK, "INTERCEPTING")
            Intercept().execute(agent)
            return True

        st = StrategyFormation().i()
        target = st.get_pos(agent.world().self().unum())
        min_dist_ball = 1000
        nearest_tm = 0
        for u in range(1, 12):
            tm = wm.our_player(u)
            if tm.unum() is not 0:
                dist = tm.pos().dist(wm.ball().pos())
                if dist < min_dist_ball:
                    min_dist_ball = dist
                    nearest_tm = u
        if nearest_tm == wm.self().unum():
            target = wm.ball().pos()
        agent.debug_client().set_target(target)
        agent.debug_client().add_message('bhv_move')
        GoToPoint(target, 1, 100).execute(agent)
        return True
