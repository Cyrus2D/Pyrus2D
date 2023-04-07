from lib.action.go_to_point import GoToPoint
from base.strategy_formation import StrategyFormation
from lib.action.intercept import Intercept
from base.tools import Tools
from base.stamina_manager import get_normal_dash_power
from pyrusgeom.soccer_math import *

from typing import TYPE_CHECKING

from lib.debug.debug import log

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent

class Bhv_Block:
    def execute(self, agent: 'PlayerAgent'):
        wm = agent.world()
        opp_min = wm.intercept_table().opponent_reach_cycle()
        ball_pos = wm.ball().inertia_point(opp_min)
        dribble_speed_etimate = 0.7
        dribble_angle_estimate = (Vector2D(-52.0, 0) - ball_pos).th()
        blocker = 0
        block_cycle = 1000
        block_pos = Vector2D(0, 0)
        for unum in range(1, 12):
            tm = wm.our_player(unum)
            if tm is None:
                continue
            if tm.unum() < 1:
                continue
            for c in range(1, 40):
                dribble_pos = ball_pos + Vector2D.polar2vector(c * dribble_speed_etimate, dribble_angle_estimate)
                turn_cycle = Tools.predict_player_turn_cycle(tm.player_type(), tm.body(), tm.vel().r(), tm.pos().dist(dribble_pos), (dribble_pos - tm.pos()).th(), 0.2, False)
                tm_cycle = tm.player_type().cycles_to_reach_distance(tm.inertia_point(opp_min).dist(dribble_pos)) + turn_cycle
                if tm_cycle <= opp_min + c:
                    if tm_cycle < block_cycle:
                        block_cycle = tm_cycle
                        blocker = unum
                        block_pos = dribble_pos
                        break
        if blocker == wm.self_unum():
            GoToPoint(block_pos, 0.1, 100).execute(agent)
            log.debug_client().add_message(f'block in ({round(block_pos.x(), 2)}, {round(block_pos.y(), 2)})')
            log.debug_client().set_target(block_pos)
            return True
        return False
