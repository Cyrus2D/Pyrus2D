from lib.action.go_to_point import *
from lib.debug.logger import *


class BhvKick:
    def __init__(self):
        pass

    def execute(self, agent):
        wm: WorldModel = agent.world()
        agent.do_kick(100,0)
