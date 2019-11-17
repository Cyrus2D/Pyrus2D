from lib.action.go_to_point import *
from lib.debug.logger import *
from lib.math.geom_2d import *
from enum import Enum
from lib.rcsc.server_param import ServerParam as SP
from lib.action.smart_kick import SmartKick
from typing import List
from base.tools import *

class KickActionType(Enum):
    No = 0
    Pass = 'Pass'
    Dribble = 'Dribble'


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
        return self.eval > other.eval

    def __repr__(self):
        return '{} Action {} to {} in {} eval:{}'.format(self.type.value, self.start_unum, self.target_unum, self.target_ball_pos, self.eval)

    def __str__(self):
        return self.__repr__()


class BhvKickGen:
    def __init__(self):
        self.candidates = []

    def can_opponent_cut_ball(self, wm: WorldModel, ball_pos, cycle):
        for unum in range(1, 12):
            opp: PlayerObject = wm.their_player(unum)
            if opp.unum() is 0:
                continue
            opp_cycle = opp.pos().dist(ball_pos) - opp.player_type().kickable_area()
            opp_cycle /= opp.player_type().real_speed_max()
            if opp_cycle < cycle:
                return True
        return False


class BhvPassGen(BhvKickGen):
    def generator(self, wm: WorldModel):
        for tm_unum in range(1, 12):
            self.generate_direct_pass(wm, tm_unum)
        return self.candidates

    def generate_direct_pass(self, wm: WorldModel, unum):
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
            if self.can_opponent_cut_ball(wm, ball_pos, cycle):
                return
        self.candidates.append(simple_direct_pass)


class BhvDribbleGen(BhvKickGen):
    def generator(self, wm: WorldModel):
        self.generate_simple_dribble(wm)
        print(self.candidates)
        return self.candidates

    def generate_simple_dribble(self, wm: WorldModel):
        angle_div = 16
        angle_step = 360.0 / angle_div

        sp = ServerParam.i()
        ptype = wm.self().player_type()

        my_first_speed = wm.self().vel().r()

        for a in range(angle_div):
            dash_angle = wm.self().body() + (angle_step * a)

            if wm.self().pos().x() < 16.0 and dash_angle.abs() > 100.0:
                continue

            if wm.self().pos().x() < -36.0 and wm.self().pos().absY() < 20.0 and dash_angle.abs() > 45.0:
                continue

            n_turn = 0

            my_speed = my_first_speed * ptype.player_decay()
            dir_diff = AngleDeg(angle_step * a).abs()

            while dir_diff > 10.0:
                dir_diff -= ptype.effective_turn(sp.max_moment(), my_speed)
                if dir_diff < 0.0:
                    dir_diff = 0.0
                my_speed *= ptype.player_decay()
                n_turn += 1

            if n_turn >= 3:
                continue

            if angle_step * a < 180.0:
                dash_angle -= dir_diff
            else:
                dash_angle += dir_diff

            self.simulate_kick_turns_dashes(wm, dash_angle, n_turn)

    def simulate_kick_turns_dashes(self, wm, dash_angle, n_turn):
        max_dash = 8
        min_dash = 2

        self_cache = []

        self.create_self_cache(wm, dash_angle, n_turn, max_dash, self_cache)

        sp = ServerParam.i()
        ptype = wm.self().player_type()

        # trap_rel = Vector2D.polar2vector(ptype.playerSize() + ptype.kickableMargin() * 0.2 + SP.ball_size(), dash_angle)
        trap_rel = Vector2D.polar2vector(ptype.player_size() + ptype.kickable_margin() * 0.2 + 0, dash_angle)

        max_x = sp.pitch_half_length() - 1.0
        max_y = sp.pitch_half_width() - 1.0

        for n_dash in range(max_dash, min_dash - 1, -1):
            ball_trap_pos = self_cache[n_turn + n_dash] + trap_rel

            if ball_trap_pos.absX() > max_x or ball_trap_pos.absY() > max_y:
                continue

            term = (1.0 - pow(sp.ball_decay(), 1 + n_turn + n_dash ) ) / (1.0 - sp.ball_decay())
            first_vel: Vector2D = (ball_trap_pos - wm.ball().pos()) / term
            print(ball_trap_pos, wm.ball().pos(), term, first_vel)
            kick_accel: Vector2D = first_vel - wm.ball().vel()
            kick_power = kick_accel.r() / wm.self().kick_rate()

            if kick_power > sp.max_power() or kick_accel.r2() > pow(sp.ball_accel_max(), 2) or first_vel.r2() > pow(
                    sp.ball_speed_max(), 2):
                continue

            if (wm.ball().pos() + first_vel).dist2(self_cache[0]) < pow(ptype.player_size() + sp.ball_size() + 0.1, 2):
                continue

            if self.check_opponent(wm, ball_trap_pos, 1 + n_turn + n_dash):
                dribble_candidate = KickAction()
                dribble_candidate.type = KickActionType.Dribble
                dribble_candidate.start_ball_pos = wm.ball().pos()
                dribble_candidate.target_ball_pos = ball_trap_pos
                dribble_candidate.target_unum = wm.self().unum()
                dribble_candidate.start_ball_speed = first_vel.r()
                self.candidates.append(dribble_candidate)

    def create_self_cache(self, wm: WorldModel, dash_angle, n_turn, n_dash, self_cache):
        sp = ServerParam.i()
        ptype = wm.self().player_type()

        self_cache.clear()

        stamina_model = wm.self().stamina_model()

        my_pos = wm.self().pos()
        my_vel = wm.self().vel()

        my_pos += my_vel
        my_vel *= ptype.player_decay()

        self_cache.append(my_pos)

        for i in range(n_turn):
            my_pos += my_vel
            my_vel *= ptype.player_decay()
            self_cache.append(my_pos)
            stamina_model.simulate_waits(ptype, 1 + n_turn)

        unit_vec = Vector2D.polar2vector(1.0, dash_angle)

        for i in range(n_dash):
                available_stamina = max(0.0, stamina_model.stamina() - sp.recover_dec_thr_value() - 300.0)
                dash_power = min(available_stamina, sp.max_dash_power())
                dash_accel = unit_vec.set_length_vector(dash_power * ptype.dash_power_rate() * stamina_model.effort())

                my_vel += dash_accel
                my_pos += my_vel
                my_vel *= ptype.player_decay()

                stamina_model.simulate_dash(ptype, dash_power)
                self_cache.append(my_pos)

    def check_opponent(self, wm: WorldModel, ball_trap_pos: Vector2D, dribble_step: int):
        sp = ServerParam.i()
        ball_move_angle:AngleDeg = (ball_trap_pos - wm.ball().pos()).th()

        for o in range(12):
            opp: PlayerObject = wm.their_player(o)
            if opp.unum() is 0:
                continue

            if opp.dist_from_self() > 20.0:
                break

            ptype = opp.player_type()

            control_area = (sp._catchable_area
                            if opp.goalie()
                               and ball_trap_pos.x() > sp.their_penalty_area_line_x()
                               and ball_trap_pos.absY() < sp.penalty_area_half_width()
                            else ptype.kickable_area())

            opp_pos = opp.inertia_point( dribble_step )

            ball_to_opp_rel = (opp.pos() - wm.ball().pos()).rotated_vector(-ball_move_angle)

            if ball_to_opp_rel.x() < -4.0:
                continue

            target_dist = opp_pos.dist(ball_trap_pos)

            if target_dist - control_area < 0.001:
                return False

            dash_dist = target_dist
            dash_dist -= control_area * 0.5
            dash_dist -= 0.2
            n_dash = ptype.cycles_to_reach_distance(dash_dist)

            n_turn = 1 if opp.body_count() > 1 else predict_player_turn_cycle(ptype,
                                                                              opp.body(),
                                                                              opp.vel().r(),
                                                                              target_dist,
                                                                              (ball_trap_pos - opp_pos).th(),
                                                                              control_area,
                                                                              True)

            n_step = n_turn + n_dash if n_turn == 0 else n_turn + n_dash + 1

            bonus_step = 0
            if ball_trap_pos.x() < 30.0:
                bonus_step += 1

            if ball_trap_pos.x() < 0.0:
                bonus_step += 1

            if opp.is_tackling():
                bonus_step = -5

            if ball_to_opp_rel.x() > 0.5:
                bonus_step += bound( 0, opp.pos_count(), 8 )
            else:
                bonus_step += bound( 0, opp.pos_count(), 4 )

            if n_step - bonus_step <= dribble_step:
                return False
        return True


class BhvKick:
    def __init__(self):
        pass

    def evaluator(self, candid: KickAction):
        return candid.target_ball_pos.x() + max(0, 40 - candid.target_ball_pos.dist(Vector2D(52, 0)))

    def execute(self, agent):
        wm: WorldModel = agent.world()
        action_candidates: List[KickAction] = []
        action_candidates += BhvPassGen().generator(wm)
        action_candidates += BhvDribbleGen().generator(wm)
        if len(action_candidates) is 0:
            return True
        for action_candidate in action_candidates:
            action_candidate.eval = self.evaluator(action_candidate)

        best_action: KickAction = max(action_candidates)

        target = best_action.target_ball_pos
        print(best_action)
        agent.debug_client().set_target(target)
        agent.debug_client().add_message(best_action.type.value + 'to ' + best_action.target_ball_pos.__str__())
        SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 1, 3).execute(agent)

