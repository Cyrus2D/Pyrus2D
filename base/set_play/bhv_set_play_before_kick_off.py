from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.angle_deg import AngleDeg
from base.strategy_formation import StrategyFormation

class Bhv_BeforeKickOff:
    def __init__(self):
        pass

    def execute(self, agent):
        unum = agent.world().self().unum()
        st = StrategyFormation.i()
        target = st.get_pos(unum)
        # dlog.add_text(Level.BLOCK, f"unum: {unum}")
        # agent.do_move(AngleDeg.cos_deg(AngleDeg.PI / 11 * unum) * 20, AngleDeg.sin_deg(AngleDeg.PI / 11 * unum) * 20) TODO not working :(
        agent.do_move(target.x(), target.y())
        return True
