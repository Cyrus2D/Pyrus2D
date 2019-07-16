from lib.player.player_agent import *
from lib.math.geom import *


class GoToPoint:
    def __init__(self, target, thr, dash_power):
        self.target = target
        self.thr = thr
        self.dash_power = dash_power

    def execute(self, agent):
        if agent.world().time().cycle() < 1:
            agent.do_move(-20, agent.world()._self_unum * 5 - 30)
            return True
        self_pos = agent.world().self().pos()
        if self_pos.dist(self.target) < self.thr:
            agent.do_turn(0)
            return True
        target_angle = (self.target - self_pos).th()
        self_body = agent.world().self().body()
        diff_angle = (target_angle - self_body).abs()
        agent.debug(f"target: {self.target}\ttarget_angle: {target_angle}")
        agent.debug(f"spos: {self_pos}\tself_body: {self_body}")
        agent.debug(f"diff_angle: {diff_angle}")
        if diff_angle < 10:
            agent.do_dash(self.dash_power, 0)
            return True

        agent.do_turn(target_angle - self_body)
        return True
