from lib.player.player_agent import *
from lib.math.geom_2d import *


class GoToPoint:
    def __init__(self, target, dist_thr, max_dash_power, dash_speed=-1.0, cycle=100, save_recovery=True, dir_thr=15.0):
        self.target = target
        self.dist_thr = dist_thr
        self.max_dash_power = max_dash_power
        self.dash_speed = dash_speed
        self.cycle = cycle
        self.save_recovery = save_recovery
        self.dir_thr = dir_thr

    def execute(self, agent: PlayerAgent):
        if self.max_dash_power < 0.1 or self.dash_speed < 0.01:
            agent.do_turn(0)
            return True

        wm: WorldModel = agent.world()
        inertia_point: Vector2D = wm.self().inertia_point(self.cycle)
        target_rel: Vector2D = self.target - inertia_point

        target_dist = target_rel.r()
        if target_dist < self.dist_thr:
            agent.do_turn(0.0)
            return False

        self_pos = agent.world().self().pos()
        if self_pos.dist(self.target) < self.thr:
            agent.do_turn(0)
            return True
        target_angle = (self.target - self_pos).th()
        self_body = agent.world().self().body()
        diff_angle = (target_angle - self_body).abs()
        if diff_angle < 10:
            agent.do_dash(self.dash_power, 0)
            return True

        agent.do_turn(target_angle - self_body)
        return True
