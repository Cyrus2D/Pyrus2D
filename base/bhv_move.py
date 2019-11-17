from lib.action.go_to_point import *
from base.strategy_formation import *
from lib.action.intercept import Intercept
from lib.debug.logger import *
from lib.player.templates import *
from base.tools import *


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
        min_cycle = 1000
        nearest_tm = 0
        for u in range(1, 12):
            tm = wm.our_player(u)
            if tm.unum() is not 0:
                tmcycle = 1000
                for i in range(40):
                    bpos = wm.ball().inertia_point(i)
                    tm_pos = tm.inertia_point(i)
                    dist = tm_pos.dist(bpos)
                    tmcycle = predict_player_turn_cycle(tm.player_type(), tm.body(), tm.vel().r(), dist, (bpos - tm.pos()).th(), 0.1, False)
                    tmcycle += tm.player_type().cycles_to_reach_distance(dist - tm.player_type().kickable_area())
                    if tmcycle <= i:
                        break
                    else:
                        tmcycle = 1000

                if tmcycle < min_cycle:
                    min_cycle = tmcycle
                    nearest_tm = u
        if nearest_tm == wm.self().unum():
            target = wm.ball().inertia_point(min_cycle)
            agent.debug_client().set_target(target)
            agent.debug_client().add_message('basic_intercept')
            GoToPoint(target, 0.1, 100).execute(agent)
            return True
        agent.debug_client().set_target(target)
        agent.debug_client().add_message('bhv_move')
        GoToPoint(target, 1, 100).execute(agent)
        return True
