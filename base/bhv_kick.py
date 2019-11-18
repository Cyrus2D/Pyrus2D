from lib.action.go_to_point import *
from lib.debug.logger import *
from lib.math.geom_2d import *
from enum import Enum
from lib.rcsc.server_param import ServerParam as SP
from lib.action.smart_kick import SmartKick
from typing import List
from base.tools import *

DEBUG_DRIBBLE = True


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
        self.index = 0

    def __gt__(self, other):
        return self.eval > other.eval

    def __repr__(self):
        return '{} Action {} to {} in {} eval:{}'.format(self.type.value, self.start_unum, self.target_unum, self.target_ball_pos, self.eval)

    def __str__(self):
        return self.__repr__()


class BhvKickGen:
    def __init__(self):
        self.candidates = []
        self.index = 0

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
        self.receivers = []
        self.update_receivers(wm)
        dlog.add_text(Level.PASS, 'receivers:{}'.format(self.receivers))
        for r in self.receivers:
            self.generate_direct_pass(wm, r)
            self.generate_lead_pass(wm, r)
            self.generate_through_pass(wm, r)
        return self.candidates

    def update_receivers(self, wm: WorldModel):
        sp = ServerParam.i()
        for unum in range(12):
            if unum == wm.self().unum():
                continue
            if wm.our_player(unum).unum() == 0:
                continue
            if wm.our_player(unum).pos_count() > 10:
                continue
            if wm.our_player(unum).is_tackling():
                continue
            if wm.our_player(unum).pos().x() > wm.offside_line_x():
                continue
            if wm.our_player(unum).goalie() and wm.our_player(unum).pos().x() < sp.our_penalty_area_line_x() + 15:
                continue
            self.receivers.append(unum)

    def generate_direct_pass(self, wm: WorldModel, t):
        sp = ServerParam.i()
        MIN_RECEIVE_STEP = 3

        MAX_DIRECT_PASS_DIST = 0.8 * inertia_final_distance(sp.ball_speed_max(), sp.ball_decay())
        MAX_RECEIVE_BALL_SPEED = sp.ball_speed_max() * pow(sp.ball_decay(), MIN_RECEIVE_STEP)
        receiver = wm.our_player(t)
        MIN_DIRECT_PASS_DIST = receiver.player_type().kickable_area() * 2.2
        if receiver.pos().x() > sp.pitch_half_length() - 1.5 or receiver.pos().x() < -sp.pitch_half_length() + 5.0 or receiver.pos().absY() > sp.pitch_half_width() - 1.5:
            dlog.add_text(Level.PASS, '#DPass to {} {}, out of field'.format(t, receiver.pos()))
            return
        # TODO sp.ourTeamGoalPos()
        if receiver.pos().x() < wm.ball().pos().x() + 1.0 and receiver.pos().dist2(Vector2D(-52.5, 0)) < pow(18.0, 2):
            dlog.add_text(Level.PASS, '#DPass to {} {}, danger near goal'.format(t, receiver.pos()))
            return

        ptype = receiver.player_type()
        max_ball_speed = wm.self().kick_rate() * sp.max_power()
        if wm.game_mode().type() == GameModeType.PlayOn:
            max_ball_speed = sp.ball_speed_max()

        # TODO SP.defaultRealSpeedMax()
        min_ball_speed = 1.0

        receive_point = ptype.inertiaFinalPoint(receiver.pos(), receiver.vel())
        ball_move_dist = wm.ball().pos().dist(receive_point)

        if ball_move_dist < MIN_DIRECT_PASS_DIST or MAX_DIRECT_PASS_DIST < ball_move_dist:
            dlog.add_text(Level.PASS, '#DPass to {} {}, far or close'.format(t, receiver.pos()))
            return

        if wm.game_mode().type() in [GameModeType.GoalKick_Left, GameModeType.GoalKick_Right] \
            and receive_point.x < sp.our_penalty_area_line_x() + 1.0 \
                and receive_point.absY() < sp.penalty_area_half_width() + 1.0:
            dlog.add_text(Level.PASS, '#DPass to {} {}, in penalty area in goal kick mode'.format(t, receiver.pos()))
            return

        max_receive_ball_speed = min(MAX_RECEIVE_BALL_SPEED, ptype.kickable_area() + (sp.max_dash_power() * ptype.dash_power_rate() * ptype.effort_max()) * 1.8)
        min_receive_ball_speed = ptype.real_speed_max()

        ball_move_angle = (receive_point - wm.ball().pos()).th()

        min_ball_step = sp.ball_move_step(sp.ball_speed_max(), ball_move_dist)
        # TODO Penalty step
        start_step = max(max(MIN_RECEIVE_STEP, min_ball_step), 0)
        max_step = start_step + 2
        dlog.add_text(Level.PASS, '#DPass to {} {}'.format(t, receiver.pos()))
        self.create_pass(wm, receiver, receive_point,
                          start_step, max_step, min_ball_speed,
                          max_ball_speed, min_receive_ball_speed,
                          max_receive_ball_speed, ball_move_dist,
                          ball_move_angle, "D")

    def generate_lead_pass(self, wm: WorldModel, t):
        pass

    def generate_through_pass(self, wm: WorldModel, t):
        pass

    def create_pass(self, wm: WorldModel, receiver, receive_point: Vector2D,
                    min_step, max_step, min_first_ball_speed, max_first_ball_speed,
                    min_receive_ball_speed, max_receive_ball_speed,
                    ball_move_dist, ball_move_angle: AngleDeg, description):
        sp = ServerParam.i()

        for step in range(min_step, max_step + 1):
            self.index += 1
            first_ball_speed = calc_first_term_geom_series(ball_move_dist, sp.ball_decay(), step)

            if first_ball_speed < min_first_ball_speed:
                dlog.add_text(Level.PASS,
                              '##Pass {},to {} {}, step:{}, ball_speed:{}, first ball speed is low'.format(self.index,
                                                                                                           receiver.unum(),
                                                                                                           receiver.pos(),
                                                                                                           step,
                                                                                                           first_ball_speed))
                break

            if max_first_ball_speed < first_ball_speed:
                dlog.add_text(Level.PASS,
                              '##Pass {},to {} {}, step:{}, ball_speed:{}, first ball speed is high'.format(self.index,
                                                                                                           receiver.unum(),
                                                                                                           receiver.pos(),
                                                                                                           step,
                                                                                                           first_ball_speed))
                continue

            receive_ball_speed = first_ball_speed * pow(sp.ball_decay(), step)

            if receive_ball_speed < min_receive_ball_speed:
                dlog.add_text(Level.PASS,
                              '##Pass {},to {} {}, step:{}, ball_speed:{}, rball_speed:{}, receive ball speed is low'.format(
                                  self.index,
                                  receiver.unum(),
                                  receiver.pos(),
                                  step,
                                  first_ball_speed,
                                  receive_ball_speed))
                break

            if max_receive_ball_speed < receive_ball_speed:
                dlog.add_text(Level.PASS,
                              '##Pass {},to {} {}, step:{}, ball_speed:{}, rball_speed:{}, receive ball speed is high'.format(
                                  self.index,
                                  receiver.unum(),
                                  receiver.pos(),
                                  step,
                                  first_ball_speed,
                                  receive_ball_speed))
                continue

            kick_count = predict_kick_count(wm, wm.self().unum(), first_ball_speed, ball_move_angle )

            o_step = self.predict_opponents_reach_step(wm, wm.ball().pos(), first_ball_speed, ball_move_angle, receive_point, step + (kick_count - 1) + 5, description)

            failed = False
            if description == 'T':
                if o_step <= step:
                    failed = True
            else:
                if o_step <= step + (kick_count - 1):
                   failed = True
            if failed:
                break

            candidate = KickAction()
            candidate.type = KickActionType.Pass
            candidate.start_ball_pos = wm.ball().pos()
            candidate.target_ball_pos = receive_point
            candidate.target_unum = receiver
            candidate.start_ball_speed = first_ball_speed
            self.candidates.append(candidate)

            find_another_pass = False
            if not find_another_pass:
                break

            if o_step <= step + 3:
                break

            if min_step + 3 <= step:
                break

    def predict_opponents_reach_step(self, wm: WorldModel, first_ball_pos: Vector2D, first_ball_speed, ball_move_angle: AngleDeg, receive_point: Vector2D, max_cycle, description):
        first_ball_vel = Vector2D.polar2vector(first_ball_speed, ball_move_angle)
        min_step = 1000
        for unum in range(12):
            opp = wm.their_player(unum)
            if opp.unum() == 0:
                continue
            step = self.predict_opponent_reach_step(wm, unum, first_ball_pos, first_ball_vel, ball_move_angle, receive_point, max_cycle, description)
            if step < min_step:
                min_step = step
        return min_step

    def predict_opponent_reach_step(self, wm: WorldModel, unum, first_ball_pos: Vector2D, first_ball_vel: Vector2D, ball_move_angle: AngleDeg, receive_point: Vector2D, max_cycle, description):
        sp = ServerParam.i()
        CONTROL_AREA_BUF = 0.15
        opponent = wm.their_player(unum)
        ptype = opponent.player_type()
        min_cycle = estimate_min_reach_cycle(opponent.pos(), ptype.real_speed_max(), first_ball_pos, ball_move_angle)

        if min_cycle < 0:
            return 1000

        for cycle in range(max( 1, min_cycle), max_cycle + 1):
            ball_pos = inertia_n_step_point(first_ball_pos, first_ball_vel, cycle, sp.ball_decay())
            control_area = ptype.kickable_area()

            inertia_pos = ptype.inertia_point(opponent.pos(), opponent.vel(), cycle)
            target_dist = inertia_pos.dist(ball_pos)

            dash_dist = target_dist
            # TODO calc Bonus
            if dash_dist - control_area - CONTROL_AREA_BUF< 0.001:
                return cycle

            dash_dist -= control_area
            if description != 'T':
                if receive_point.x() < 25:
                    dash_dist -= 0.5
                else:
                    dash_dist -= 0.2
            if dash_dist > ptype.real_speed_max() * (cycle + min(opponent.pos_count(), 5)):
                continue

            n_dash = ptype.cycles_to_reach_distance(dash_dist)
            if n_dash > cycle + opponent.pos_count():
              continue

            n_turn = 0
            if opponent.body_count() > 1:
                n_turn = predict_player_turn_cycle(ptype, opponent.body(), opponent.vel().r(), target_dist, (ball_pos - inertia_pos).th(), control_area, True)

            n_step = n_turn + n_dash if n_turn == 0 else n_turn + n_dash + 1

            bonus_step = 0
            if opponent.is_tackling():
                bonus_step = -5
            if n_step - bonus_step <= cycle:
                return cycle
        return 1000


class BhvDribbleGen(BhvKickGen):
    def generator(self, wm: WorldModel):
        self.debug_dribble = []
        self.generate_simple_dribble(wm)

        if DEBUG_DRIBBLE:
            for dribble in self.debug_dribble:
                if dribble[2]:
                    dlog.add_message(Level.DRIBBLE, dribble[1].x(), dribble[1].y(), '{}'.format(dribble[0]))
                    dlog.add_circle(Level.DRIBBLE, cicle=Circle2D(dribble[1], 0.2),
                                    color=Color(string='green'))
                else:
                    dlog.add_message(Level.DRIBBLE, dribble[1].x(), dribble[1].y(), '{}'.format(dribble[0]))
                    dlog.add_circle(Level.DRIBBLE, cicle=Circle2D(dribble[1], 0.2),
                                    color=Color(string='red'))

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
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE, '#dash angle:{} cancel is not safe1'.format(dash_angle))
                continue

            if wm.self().pos().x() < -36.0 and wm.self().pos().absY() < 20.0 and dash_angle.abs() > 45.0:
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE, '#dash angle:{} cancel is not safe2'.format(dash_angle))
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
            if DEBUG_DRIBBLE:
                dlog.add_text(Level.DRIBBLE, '#dash angle:{} turn:{}'.format(dash_angle, n_turn))
            self.simulate_kick_turns_dashes(wm, dash_angle, n_turn)

    def simulate_kick_turns_dashes(self, wm, dash_angle, n_turn):
        max_dash = 8
        min_dash = 2

        self_cache = []

        self.create_self_cache(wm, dash_angle, n_turn, max_dash, self_cache)
        if DEBUG_DRIBBLE:
            dlog.add_text(Level.DRIBBLE, '##self_cache:{}'.format(self_cache))
        sp = ServerParam.i()
        ptype = wm.self().player_type()

        # trap_rel = Vector2D.polar2vector(ptype.playerSize() + ptype.kickableMargin() * 0.2 + SP.ball_size(), dash_angle)
        trap_rel = Vector2D.polar2vector(ptype.player_size() + ptype.kickable_margin() * 0.2 + 0, dash_angle)

        max_x = sp.pitch_half_length() - 1.0
        max_y = sp.pitch_half_width() - 1.0

        for n_dash in range(max_dash, min_dash - 1, -1):
            self.index += 1
            ball_trap_pos = self_cache[n_turn + n_dash] + trap_rel

            if ball_trap_pos.absX() > max_x or ball_trap_pos.absY() > max_y:
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE,
                                  '#index:{} target:{} our of field'.format(self.index, ball_trap_pos))
                    self.debug_dribble.append((self.index, ball_trap_pos, False))
                continue

            term = (1.0 - pow(sp.ball_decay(), 1 + n_turn + n_dash ) ) / (1.0 - sp.ball_decay())
            first_vel: Vector2D = (ball_trap_pos - wm.ball().pos()) / term
            kick_accel: Vector2D = first_vel - wm.ball().vel()
            kick_power = kick_accel.r() / wm.self().kick_rate()

            if kick_power > sp.max_power() or kick_accel.r2() > pow(sp.ball_accel_max(), 2) or first_vel.r2() > pow(
                    sp.ball_speed_max(), 2):
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE,
                                  '#index:{} target:{} need more power, power:{}, accel:{}, vel:{}'.format(
                                      self.index, ball_trap_pos, kick_power, kick_accel, first_vel))
                    self.debug_dribble.append((self.index, ball_trap_pos, False))
                continue

            if (wm.ball().pos() + first_vel).dist2(self_cache[0]) < pow(ptype.player_size() + sp.ball_size() + 0.1, 2):
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE,
                                  '#index:{} target:{} in body, power:{}, accel:{}, vel:{}'.format(
                                      self.index, ball_trap_pos, kick_power, kick_accel, first_vel))
                self.debug_dribble.append((self.index, ball_trap_pos, False))
                continue

            if self.check_opponent(wm, ball_trap_pos, 1 + n_turn + n_dash):
                dribble_candidate = KickAction()
                dribble_candidate.type = KickActionType.Dribble
                dribble_candidate.start_ball_pos = wm.ball().pos()
                dribble_candidate.target_ball_pos = ball_trap_pos
                dribble_candidate.target_unum = wm.self().unum()
                dribble_candidate.start_ball_speed = first_vel.r()
                dribble_candidate.index = self.index
                self.candidates.append(dribble_candidate)
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE,
                                  '#index:{} target:{}, power:{}, accel:{}, vel:{} OK'.format(
                                      self.index, ball_trap_pos, kick_power, kick_accel, first_vel))
                    self.debug_dribble.append((self.index, ball_trap_pos, True))
            else:
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE,
                                  '#index:{} target:{}, power:{}, accel:{}, vel:{} Opponent catch it'.format(
                                      self.index, ball_trap_pos, kick_power, kick_accel, first_vel))
                    self.debug_dribble.append((self.index, ball_trap_pos, False))

    def create_self_cache(self, wm: WorldModel, dash_angle, n_turn, n_dash, self_cache):
        sp = ServerParam.i()
        ptype = wm.self().player_type()

        self_cache.clear()

        stamina_model = wm.self().stamina_model()

        my_pos = wm.self().pos()
        my_vel = wm.self().vel()

        my_pos += my_vel
        my_vel *= ptype.player_decay()

        self_cache.append(Vector2D(vector2d=my_pos))

        for i in range(n_turn):
            my_pos += my_vel
            my_vel *= ptype.player_decay()
            self_cache.append(Vector2D(vector2d=my_pos))
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
                self_cache.append(Vector2D(vector2d=my_pos))

    def check_opponent(self, wm: WorldModel, ball_trap_pos: Vector2D, dribble_step: int):
        sp = ServerParam.i()
        ball_move_angle:AngleDeg = (ball_trap_pos - wm.ball().pos()).th()

        for o in range(12):
            opp: PlayerObject = wm.their_player(o)
            if opp.unum() is 0:
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE, "###OPP {} is ghost".format(o))
                continue

            if opp.dist_from_self() > 20.0:
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE, "###OPP {} is far".format(o))
                continue

            ptype = opp.player_type()

            control_area = (sp._catchable_area
                            if opp.goalie()
                               and ball_trap_pos.x() > sp.their_penalty_area_line_x()
                               and ball_trap_pos.absY() < sp.penalty_area_half_width()
                            else ptype.kickable_area())

            opp_pos = opp.inertia_point( dribble_step )

            ball_to_opp_rel = (opp.pos() - wm.ball().pos()).rotated_vector(-ball_move_angle)

            if ball_to_opp_rel.x() < -4.0:
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE, "###OPP {} is behind".format(o))
                continue

            target_dist = opp_pos.dist(ball_trap_pos)

            if target_dist - control_area < 0.001:
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE, "###OPP {} Catch, ball will be in his body".format(o))
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
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE,
                                  "###OPP {} catch n_step:{}, dr_step:{}, bonas:{}".format(o, n_step, dribble_step,
                                                                                       bonus_step))
                return False
            else:
                if DEBUG_DRIBBLE:
                    dlog.add_text(Level.DRIBBLE,
                                  "###OPP {} can't catch n_step:{}, dr_step:{}, bonas:{}".format(o, n_step, dribble_step,
                                                                                           bonus_step))
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
        agent.debug_client().add_message(best_action.type.value + 'to ' + best_action.target_ball_pos.__str__() + ' ' + str(best_action.start_ball_speed))
        SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 1, 3).execute(agent)

