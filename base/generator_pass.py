from lib.debug.logger import dlog, Level, Color
from lib.math.geom_2d import *
import lib.math.soccer_math as smath
from lib.player.templates import *
from lib.rcsc.server_param import ServerParam as SP
from base.tools import Tools
import time
from base.generator_action import KickAction, KickActionType, BhvKickGen


debug_pass = False
max_pass_time = 0


class BhvPassGen(BhvKickGen):
    def generator(self, wm: WorldModel):
        global max_pass_time
        self.best_pass = None
        start_time = time.time()
        self.receivers = []
        self.update_receivers(wm)
        dlog.add_text(Level.PASS, 'receivers:{}'.format(self.receivers))
        for r in self.receivers:
            if self.best_pass is not None \
                    and wm.our_player(r).pos().x() < self.best_pass.target_ball_pos.x() - 5:
                break
            self.generate_direct_pass(wm, r)
            self.generate_lead_pass(wm, r)
            self.generate_through_pass(wm, r)

        if debug_pass:
            for candid in self.debug_list:
                if candid[2]:
                    dlog.add_message(Level.PASS, candid[1].x(), candid[1].y(), '{}'.format(candid[0]))
                    dlog.add_circle(Level.PASS, cicle=Circle2D(candid[1], 0.2),
                                    color=Color(string='green'))
                else:
                    dlog.add_message(Level.PASS, candid[1].x(), candid[1].y(), '{}'.format(candid[0]))
                    dlog.add_circle(Level.PASS, cicle=Circle2D(candid[1], 0.2),
                                    color=Color(string='red'))
        end_time = time.time()
        if end_time - start_time > max_pass_time:
            max_pass_time = end_time - start_time
        dlog.add_text(Level.PASS, 'time:{} max is {}'.format(end_time - start_time, max_pass_time))
        return self.candidates

    def update_receivers(self, wm: WorldModel):
        sp = SP.i()
        for unum in range(1, 12):
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
        self.receivers = sorted(self.receivers, key=lambda unum: wm.our_player(unum).pos().x(), reverse=True)

    def generate_direct_pass(self, wm: WorldModel, t):
        sp = SP.i()
        min_receive_step = 3
        max_direct_pass_dist = 0.8 * smath.inertia_final_distance(sp.ball_speed_max(), sp.ball_decay())
        max_receive_ball_speed = sp.ball_speed_max() * pow(sp.ball_decay(), min_receive_step)
        receiver = wm.our_player(t)
        min_direct_pass_dist = receiver.player_type().kickable_area() * 2.2
        if receiver.pos().x() > sp.pitch_half_length() - 1.5 \
                or receiver.pos().x() < -sp.pitch_half_length() + 5.0 \
                or receiver.pos().absY() > sp.pitch_half_width() - 1.5:
            if debug_pass:
                dlog.add_text(Level.PASS, '#DPass to {} {}, out of field'.format(t, receiver.pos()))
            return
        # TODO sp.ourTeamGoalPos()
        if receiver.pos().x() < wm.ball().pos().x() + 1.0 \
                and receiver.pos().dist2(Vector2D(-52.5, 0)) < pow(18.0, 2):
            if debug_pass:
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

        if ball_move_dist < min_direct_pass_dist or max_direct_pass_dist < ball_move_dist:
            if debug_pass:
                dlog.add_text(Level.PASS, '#DPass to {} {}, far or close'.format(t, receiver.pos()))
            return

        if wm.game_mode().type() in [GameModeType.GoalKick_Left, GameModeType.GoalKick_Right] \
                and receive_point.x < sp.our_penalty_area_line_x() + 1.0 \
                and receive_point.absY() < sp.penalty_area_half_width() + 1.0:
            if debug_pass:
                dlog.add_text(Level.PASS,
                              '#DPass to {} {}, in penalty area in goal kick mode'.format(t, receiver.pos()))
            return

        max_receive_ball_speed = min(max_receive_ball_speed, ptype.kickable_area() + (
                    sp.max_dash_power() * ptype.dash_power_rate() * ptype.effort_max()) * 1.8)
        min_receive_ball_speed = ptype.real_speed_max()

        ball_move_angle = (receive_point - wm.ball().pos()).th()

        min_ball_step = sp.ball_move_step(sp.ball_speed_max(), ball_move_dist)
        # TODO Penalty step
        start_step = max(max(min_receive_step, min_ball_step), 0)
        max_step = start_step + 2
        dlog.add_text(Level.PASS, '#DPass to {} {}'.format(t, receiver.pos()))
        self.create_pass(wm, receiver, receive_point,
                         start_step, max_step, min_ball_speed,
                         max_ball_speed, min_receive_ball_speed,
                         max_receive_ball_speed, ball_move_dist,
                         ball_move_angle, "D")

    def generate_lead_pass(self, wm: WorldModel, t):
        sp = SP.i()
        our_goal_dist_thr2 = pow(16.0, 2)
        min_receive_step = 4
        max_receive_step = 20
        min_leading_pass_dist = 3.0
        max_leading_pass_dist = 0.8 * smath.inertia_final_distance(sp.ball_speed_max(), sp.ball_decay())
        max_receive_ball_speed = sp.ball_speed_max() * pow(sp.ball_decay(), min_receive_step)

        max_player_distance = 35
        receiver = wm.our_player(t)
        if receiver.pos().dist(wm.ball().pos()) > max_player_distance:
            if debug_pass:
                dlog.add_text(Level.PASS, '#LPass to {} {}, player is far'.format(t, receiver.pos()))
            return

        abgle_divs = 8
        angle_step = 360.0 / abgle_divs
        dist_divs = 4
        dist_step = 1.1

        ptype = receiver.player_type()
        max_ball_speed = wm.self().kick_rate() * sp.max_power()
        if wm.game_mode().type() == GameModeType.PlayOn:
            max_ball_speed = sp.ball_speed_max()
        min_ball_speed = sp.default_player_speed_max()

        max_receive_ball_speed = min(max_receive_ball_speed, ptype.kickable_area() + (
                    sp.max_dash_power() * ptype.dash_power_rate() * ptype.effort_max()) * 1.5)
        min_receive_ball_speed = 0.001

        our_goal = Vector2D(-52.5, 0)

        angle_from_ball = (receiver.pos() - wm.ball().pos()).th()
        for d in range(1, dist_divs + 1):
            player_move_dist = dist_step * d
            a_step = 2 if player_move_dist * 2.0 * math.pi / abgle_divs < 0.6 else 1
            for a in range(abgle_divs + 1):
                angle = angle_from_ball + angle_step * a
                receive_point = receiver.inertia_point(1) + Vector2D.from_polar(player_move_dist, angle)

                move_dist_penalty_step = 0
                ball_move_line = Line2D(wm.ball().pos(), receive_point)
                player_line_dist = ball_move_line.dist(receiver.pos())
                move_dist_penalty_step = int(player_line_dist * 0.3)
                if receive_point.x() > sp.pitch_half_length() - 3.0 \
                        or receive_point.x() < -sp.pitch_half_length() + 5.0 \
                        or receive_point.absY() > sp.pitch_half_width() - 3.0:
                    if debug_pass:
                        dlog.add_text(Level.PASS, '#LPass to {} {}, out of field'.format(t, receive_point))
                    continue

                if receive_point.x() < wm.ball().pos().x() \
                        and receive_point.dist2(our_goal) < our_goal_dist_thr2:
                    if debug_pass:
                        dlog.add_text(Level.PASS, '#LPass to {} {}, pass is danger'.format(t, receive_point))
                    continue

                if wm.game_mode().type() in [GameModeType.GoalKick_Right, GameModeType.GoalKick_Left] \
                        and receive_point.x() < sp.our_penalty_area_line_x() + 1.0 \
                        and receive_point.absY() < sp.penalty_area_half_width() + 1.0:
                    if debug_pass:
                        dlog.add_text(Level.PASS, '#LPass to {} {}, in penalty area'.format(t, receive_point))
                    return

                ball_move_dist = wm.ball().pos().dist(receive_point)

                if ball_move_dist < min_leading_pass_dist or max_leading_pass_dist < ball_move_dist:
                    if debug_pass:
                        dlog.add_text(Level.PASS, '#LPass to {} {}, so far or so close'.format(t, receive_point))
                    continue

                nearest_receiver_unum = Tools.get_nearest_teammate_unum(wm, receive_point, self.receivers)
                if nearest_receiver_unum != t:
                    if debug_pass:
                        dlog.add_text(Level.PASS,
                                      '#LPass to {} {}, {} is closer than receiver '.format(t, receive_point,
                                                                                            nearest_receiver_unum))
                    continue

                receiver_step = self.predict_receiver_reach_step(receiver, receive_point, True,
                                                                 'L') + move_dist_penalty_step
                ball_move_angle = (receive_point - wm.ball().pos()).th()

                min_ball_step = sp.ball_move_step(sp.ball_speed_max(), ball_move_dist)

                start_step = max(max(min_receive_step, min_ball_step), receiver_step)
                # ifdef CREATE_SEVERAL_CANDIDATES_ON_SAME_POINT
                # max_step = std::max(max_receive_step, start_step + 3);
                # else
                if debug_pass:
                    dlog.add_text(Level.PASS, '#LPass to {} {}'.format(t, receive_point))
                max_step = start_step + 3
                self.create_pass(wm, receiver, receive_point,
                                 start_step, max_step,
                                 min_ball_speed, max_ball_speed,
                                 min_receive_ball_speed, max_receive_ball_speed,
                                 ball_move_dist, ball_move_angle,
                                 'L')

    def generate_through_pass(self, wm: WorldModel, t):
        pass

    def predict_receiver_reach_step(self, receiver, pos: Vector2D, use_penalty, pass_type):
        ptype = receiver.player_type()

        target_dist = receiver.inertia_point(1).dist(pos)
        n_turn = 1 if receiver.body_count() > 0 else Tools.predict_player_turn_cycle(ptype, receiver.body(),
                                                                                     receiver.vel().r(), target_dist, (
                                                                                                 pos - receiver.inertia_point(
                                                                                             1)).th(),
                                                                                     ptype.kickable_area(), False)
        dash_dist = target_dist

        # if use_penalty:
        #     dash_dist += receiver.penalty_distance_;

        if pass_type == 'L':
            dash_dist *= 1.05

            dash_angle = (pos - receiver.pos()).th()

            if dash_angle.abs() > 90.0 or receiver.body_count() > 1 or (dash_angle - receiver.body()).abs() > 30.0:
                n_turn += 1

        n_dash = ptype.cycles_to_reach_distance(dash_dist)

        n_step = n_turn + n_dash if n_turn == 0 else n_turn + n_dash + 1
        return n_step

    def create_pass(self, wm: WorldModel, receiver, receive_point: Vector2D,
                    min_step, max_step, min_first_ball_speed, max_first_ball_speed,
                    min_receive_ball_speed, max_receive_ball_speed,
                    ball_move_dist, ball_move_angle: AngleDeg, description):
        sp = SP.i()

        for step in range(min_step, max_step + 1):
            self.index += 1
            first_ball_speed = smath.calc_first_term_geom_series(ball_move_dist, sp.ball_decay(), step)

            if first_ball_speed < min_first_ball_speed:
                if debug_pass:
                    dlog.add_text(Level.PASS,
                                  '##Pass {},to {} {}, step:{}, ball_speed:{}, first ball speed is low'.format(
                                      self.index,
                                      receiver.unum(),
                                      receiver.pos(),
                                      step,
                                      first_ball_speed))
                    self.debug_list.append((self.index, receive_point, False))
                break

            if max_first_ball_speed < first_ball_speed:
                if debug_pass:
                    dlog.add_text(Level.PASS,
                                  '##Pass {},to {} {}, step:{}, ball_speed:{}, first ball speed is high'.format(
                                      self.index,
                                      receiver.unum(),
                                      receiver.pos(),
                                      step,
                                      first_ball_speed))
                    self.debug_list.append((self.index, receive_point, False))
                continue

            receive_ball_speed = first_ball_speed * pow(sp.ball_decay(), step)

            if receive_ball_speed < min_receive_ball_speed:
                if debug_pass:
                    dlog.add_text(Level.PASS,
                                  '##Pass {},to {} {}, step:{}, ball_speed:{}, rball_speed:{}, receive ball speed is low'.format(
                                      self.index,
                                      receiver.unum(),
                                      receiver.pos(),
                                      step,
                                      first_ball_speed,
                                      receive_ball_speed))
                    self.debug_list.append((self.index, receive_point, False))
                break

            if max_receive_ball_speed < receive_ball_speed:
                if debug_pass:
                    dlog.add_text(Level.PASS,
                                  '##Pass {},to {} {}, step:{}, ball_speed:{}, rball_speed:{}, receive ball speed is high'.format(
                                      self.index,
                                      receiver.unum(),
                                      receiver.pos(),
                                      step,
                                      first_ball_speed,
                                      receive_ball_speed))
                    self.debug_list.append((self.index, receive_point, False))
                continue

            kick_count = Tools.predict_kick_count(wm, wm.self().unum(), first_ball_speed, ball_move_angle)

            o_step, o_unum = self.predict_opponents_reach_step(wm, wm.ball().pos(), first_ball_speed, ball_move_angle,
                                                               receive_point, step + (kick_count - 1) + 5, description)

            failed = False
            if description == 'T':
                if o_step <= step:
                    failed = True
            else:
                if o_step <= step + (kick_count - 1):
                    failed = True
            if failed:
                if debug_pass:
                    dlog.add_text(Level.PASS,
                                  '#Pass {} Failed,to {} {}, opp {} step {} max_step {}'.format(self.index,
                                                                                                receiver.unum(),
                                                                                                receive_point, o_unum,
                                                                                                o_step,
                                                                                                max_step))
                    self.debug_list.append((self.index, receive_point, False))
                break
            if debug_pass:
                dlog.add_text(Level.PASS,
                              '#Pass {} OK,to {} {}, opp {} step {} max_step {}'.format(self.index, receiver.unum(),
                                                                                        receive_point, o_unum, o_step,
                                                                                        max_step))
            self.debug_list.append((self.index, receive_point, True))
            candidate = KickAction()
            candidate.type = KickActionType.Pass
            candidate.start_ball_pos = wm.ball().pos()
            candidate.target_ball_pos = receive_point
            candidate.target_unum = receiver
            candidate.start_ball_speed = first_ball_speed
            candidate.evaluate()
            self.candidates.append(candidate)

            if self.best_pass is None or candidate.eval > self.best_pass.eval:
                self.best_pass = candidate

            find_another_pass = False
            if not find_another_pass:
                break

            if o_step <= step + 3:
                break

            if min_step + 3 <= step:
                break

    def predict_opponents_reach_step(self, wm: WorldModel, first_ball_pos: Vector2D, first_ball_speed,
                                     ball_move_angle: AngleDeg, receive_point: Vector2D, max_cycle, description):
        first_ball_vel = Vector2D.polar2vector(first_ball_speed, ball_move_angle)
        min_step = 1000
        min_opp = 0
        for unum in range(12):
            opp = wm.their_player(unum)
            if opp.unum() == 0:
                continue
            step = self.predict_opponent_reach_step(wm, unum, first_ball_pos, first_ball_vel, ball_move_angle,
                                                    receive_point, max_cycle, description)
            if step < min_step:
                min_step = step
                min_opp = unum
        return min_step, min_opp

    def predict_opponent_reach_step(self, wm: WorldModel, unum, first_ball_pos: Vector2D, first_ball_vel: Vector2D,
                                    ball_move_angle: AngleDeg, receive_point: Vector2D, max_cycle, description):
        sp = SP.i()
        CONTROL_AREA_BUF = 0.15
        opponent = wm.their_player(unum)
        ptype = opponent.player_type()
        min_cycle = Tools.estimate_min_reach_cycle(opponent.pos(), ptype.real_speed_max(), first_ball_pos,
                                                   ball_move_angle)

        if min_cycle < 0:
            return 1000

        for cycle in range(max(1, min_cycle), max_cycle + 1):
            ball_pos = smath.inertia_n_step_point(first_ball_pos, first_ball_vel, cycle, sp.ball_decay())
            control_area = ptype.kickable_area()

            inertia_pos = ptype.inertia_point(opponent.pos(), opponent.vel(), cycle)
            target_dist = inertia_pos.dist(ball_pos)

            dash_dist = target_dist
            # TODO calc Bonus
            if dash_dist - control_area - CONTROL_AREA_BUF < 0.001:
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
                n_turn = Tools.predict_player_turn_cycle(ptype, opponent.body(), opponent.vel().r(), target_dist,
                                                         (ball_pos - inertia_pos).th(), control_area, True)

            n_step = n_turn + n_dash if n_turn == 0 else n_turn + n_dash + 1

            bonus_step = 0
            if opponent.is_tackling():
                bonus_step = -5
            if n_step - bonus_step <= cycle:
                return cycle
        return 1000

