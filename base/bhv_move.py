from lib.action.go_to_point import GoToPoint
from base.strategy_formation import StrategyFormation
from lib.action.intercept import Intercept
from lib.action.turn_to_ball import TurnToBall
from lib.action.turn_to_point import TurnToPoint
from lib.debug.logger import dlog, Level
from base.tools import Tools
from base.stamina_manager import get_normal_dash_power
from base.bhv_block import Bhv_Block
from pyrusgeom.vector_2d import Vector2D

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent
    from lib.player.world_model import WorldModel

class BhvMove:
    def __init__(self):
        pass

    def execute(self, agent: 'PlayerAgent'):
        wm: 'WorldModel' = agent.world()
        
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
            agent.debug_client().add_message('intercept')
            if Intercept().execute(agent):
                return True

        if opp_min < min(tm_min, self_min):
            if Bhv_Block().execute(agent):
                return True
        st = StrategyFormation().i()
        target = st.get_pos(agent.world().self().unum())

        agent.debug_client().set_target(target)
        agent.debug_client().add_message('bhv_move')

        dash_power = get_normal_dash_power(wm)
        dist_thr = wm.ball().dist_from_self() * 0.1

        if dist_thr < 1.0:
            dist_thr = 1.0

        if wm.ball().pos_valid() and GoToPoint(target, dist_thr, dash_power).execute(agent):
            return True
        if TurnToBall().execute(agent):
            return True
        return TurnToPoint(Vector2D(0,0)).execute(agent)
            
