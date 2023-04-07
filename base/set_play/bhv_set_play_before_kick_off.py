from lib.action.neck_scan_field import NeckScanField
from lib.action.scan_field import ScanField
from lib.debug.level import Level
from pyrusgeom.angle_deg import AngleDeg
from base.strategy_formation import StrategyFormation

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent
class Bhv_BeforeKickOff:
    def __init__(self):
        pass

    def execute(self, agent: 'PlayerAgent'):
        unum = agent.world().self().unum()
        st = StrategyFormation.i()
        target = st.get_pos(unum)
        if target.dist(agent.world().self().pos()) > 1.:
            agent.do_move(target.x(), target.y())
            agent.set_neck_action(NeckScanField())
            return True
        ScanField().execute(agent)
        return True
