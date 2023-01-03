from lib.debug.level import Level
from lib.debug.logger import dlog
from pyrusgeom.angle_deg import AngleDeg
from base.strategy_formation import StrategyFormation

class Bhv_BeforeKickOff:
    def __init__(self):
        pass

    def execute(self, agent):
        unum = agent.world().self().unum()
        st = StrategyFormation.i()
        target = st.get_pos(unum)
        agent.do_move(target.x(), target.y())
        return True
