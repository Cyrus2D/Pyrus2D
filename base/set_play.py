from lib.action.go_to_point import *
from base.strategy import *
from lib.debug.logger import *


class SetPlay:
    def __init__(self):
        pass

    def execute(self, agent):
        st = Strategy()
        wm: WorldModel = agent.world()

        if agent.world().time().cycle() < 1:
            agent.do_move(-20, wm.self().unum() * 5 - 30)
            return True
