from lib.action.go_to_point import *
from lib.debug.logger import *
from lib.math.geom_2d import *
from enum import Enum
from lib.rcsc.server_param import ServerParam as SP
from lib.action.smart_kick import SmartKick
from typing import List


class KickActionType(Enum):
    No = 0
    Pass = 1
    Dribble = 2


class KickAction:
    def __init__(self):
        self.target_ball_pos = Vector2D.invalid()
        self.start_ball_pos = Vector2D.invalid()
        self.target_unum = 0
        self.start_unum = 0
        self.start_ball_speed = 0
        self.type = KickActionType.No
        self.eval = 0

    def __gt__(self, other):
        return self.eval < other.eval

    def __repr__(self):
        return 'KAction {} to {} in {} eval:{}'.format(self.start_unum, self.target_unum, self.target_ball_pos, self.eval)

    def __str__(self):
        return self.__repr__()


class BhvPassGen:
    def __init__(self):
        pass

    def generator(self, wm: WorldModel, action_candidates):
        for tm_unum in range(1, 12):
            self.generate_direct_pass(wm, tm_unum, action_candidates)

    def generate_direct_pass(self, wm: WorldModel, unum, action_candidates):
        simple_direct_pass = KickAction()
        if wm.our_player(unum).unum() is 0:
            return
        tm = wm.our_player(unum)
        if tm.unum() == wm.self().unum():
            return
        intercept_cycle = 0
        if wm.self().is_kickable():
            intercept_cycle = 0
        simple_direct_pass.type = KickActionType.Pass
        simple_direct_pass.start_ball_pos = wm.ball().pos()
        simple_direct_pass.target_ball_pos = tm.pos()
        simple_direct_pass.target_unum = unum
        simple_direct_pass.start_ball_speed = 2.0

        pass_dist = simple_direct_pass.start_ball_pos.dist(simple_direct_pass.target_ball_pos)
        ball_speed = simple_direct_pass.start_ball_speed
        ball_vel: Vector2D = Vector2D.polar2vector(ball_speed, (
                simple_direct_pass.target_ball_pos - simple_direct_pass.start_ball_pos).th())
        # print(type(ball_vel))
        ball_pos: Vector2D = simple_direct_pass.start_ball_pos
        travel_dist = 0
        cycle = 0
        # print(ball_pos)
        # print(simple_direct_pass.target_ball_pos)
        # print(pass_dist)
        while travel_dist < pass_dist and ball_speed >= 0.1:
            # dlog.add_circle(Level.PASS, Circle2D(ball_pos, 1.0))
            cycle += 1
            travel_dist += ball_speed
            ball_speed *= SP.i().ball_decay()
            ball_pos += ball_vel
            ball_vel.set_length(ball_speed)
            if self.can_opps_cut_ball(wm, ball_pos, cycle):
                return
        action_candidates.append(simple_direct_pass)

    def can_opps_cut_ball(self, wm: WorldModel, ball_pos, cycle):
        for unum in range(1, 12):
            opp: PlayerObject = wm.their_player(unum)
            if opp.unum() is 0:
                continue
            opp_cycle = opp.pos().dist(ball_pos) - opp.player_type().kickable_area()
            opp_cycle /= opp.player_type().real_speed_max()
            if opp_cycle < cycle:
                return True
        return False


class BhvDribbleGen:
    def __init__(self):
        pass

    def generator(self, wm: WorldModel, action_candidates):
        pass

    def generate_direct_pass(self, wm: WorldModel, unum, action_candidates):
        pass


class BhvKick:
    def __init__(self):
        pass

    def evaluator(self, candid: KickAction):
        return candid.target_ball_pos.x() + max(0, 40 - candid.target_ball_pos.dist(Vector2D(52, 0)))

    def execute(self, agent):
        wm: WorldModel = agent.world()
        action_candidates: List[KickAction] = []
        BhvPassGen().generator(wm, action_candidates)
        if len(action_candidates) is 0:
            return True
        for action_candidate in action_candidates:
            action_candidate.eval = self.evaluator(action_candidate)

        best_action: KickAction = max(action_candidates)

        target = best_action.target_ball_pos
        print("target len:", len(action_candidates), "Target :", target , " Speed : " , best_action.start_ball_speed)
        SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 1, 3).execute(agent)  # best_action.start_ball_speed, 0.7, 3).execute(agent)

        # agent.do_kick(100, angle)
