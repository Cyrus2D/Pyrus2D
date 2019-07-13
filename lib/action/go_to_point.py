from lib.Player.player_agent import *
from lib.math.geom import *


class GoToPoint:
    def __init__(self, target, thr, dash_power):
        self.target = target
        self.thr = thr
        self.dash_power = dash_power

    def execute(self, agent):
        self_pos = agent.world().self().pos()
        if self_pos.dist(self.target) < self.thr:
            agent.do_turn(0)
            return True
        ball_angle = (self.target - self_pos).th()
        self_body = agent.world().self().body()
        diff_angle = (ball_angle - self_body).abs()
        if diff_angle < 10:
            agent.do_dash(0, self.dash_power)
            return True

        agent.do_turn(ball_angle - self_body)
        return True
