from base.basic_tackle import BasicTackle
from lib.action.go_to_point import GoToPoint
from base.strategy_formation import StrategyFormation
from lib.action.intercept import Intercept
from lib.action.neck_turn_to_ball import NeckTurnToBall
from lib.action.neck_turn_to_ball_or_scan import NeckTurnToBallOrScan
from lib.action.turn_to_ball import TurnToBall
from lib.action.turn_to_point import TurnToPoint
from base.tools import Tools
from base.stamina_manager import get_normal_dash_power
from base.bhv_block import Bhv_Block
from pyrusgeom.vector_2d import Vector2D

from typing import TYPE_CHECKING

from lib.debug.debug import log

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent
    from lib.player.world_model import WorldModel


class BhvMove:
    def __init__(self):
        self._in_recovery_mode = False
        pass

    def execute(self, agent: 'PlayerAgent'):
        wm: 'WorldModel' = agent.world()

        if BasicTackle(0.8, 80).execute(agent):
            return True
        
        # intercept
        self_min = wm.intercept_table().self_reach_cycle()
        tm_min = wm.intercept_table().teammate_reach_cycle()
        opp_min = wm.intercept_table().opponent_reach_cycle()
        log.sw_log().block().add_text(
                      f"self_min={self_min}")
        log.sw_log().block().add_text(
                      f"tm_min={tm_min}")
        log.sw_log().block().add_text(
                      f"opp_min={opp_min}")

        if (not wm.exist_kickable_teammates()
                and (self_min <= 2
                    or (self_min <= tm_min
                        and self_min < opp_min + 5))):
            log.sw_log().block().add_text( "INTERCEPTING")
            log.debug_client().add_message('intercept')
            if Intercept().execute(agent):
                agent.set_neck_action(NeckTurnToBall())
                return True

        if opp_min < min(tm_min, self_min):
            if Bhv_Block().execute(agent):
                agent.set_neck_action(NeckTurnToBall())
                return True
        st = StrategyFormation().i()
        target = st.get_pos(agent.world().self().unum())

        log.debug_client().set_target(target)
        log.debug_client().add_message('bhv_move')

        dash_power, self._in_recovery_mode = get_normal_dash_power(wm, self._in_recovery_mode)
        dist_thr = wm.ball().dist_from_self() * 0.1

        if dist_thr < 1.0:
            dist_thr = 1.0

        if GoToPoint(target, dist_thr, dash_power).execute(agent):
            agent.set_neck_action(NeckTurnToBallOrScan())
            return True
        return False
            
