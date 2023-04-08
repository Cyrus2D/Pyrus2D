from pyrusgeom.geom_2d import *
import pyrusgeom.soccer_math as smath

from lib.debug.debug import log
from lib.rcsc.server_param import ServerParam as SP
from base.tools import Tools
import time
from base.generator_action import BhvKickGen, KickActionType, KickAction

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.object_player import PlayerObject

debug_dribble = False
max_dribble_time = 0


class BhvDribbleGen(BhvKickGen):
    def generator(self, wm: 'WorldModel'):
        global max_dribble_time
        start_time = time.time()
        self.generate_simple_dribble(wm)

        if debug_dribble:
            for dribble in self.debug_list:
                if dribble[2]:
                    log.sw_log().dribble().add_message( dribble[1].x(), dribble[1].y(), '{}'.format(dribble[0]))
                    log.sw_log().dribble().add_circle( cicle=Circle2D(dribble[1], 0.2),
                                    color=Color(string='green'))
                else:
                    log.sw_log().dribble().add_message( dribble[1].x(), dribble[1].y(), '{}'.format(dribble[0]))
                    log.sw_log().dribble().add_circle( cicle=Circle2D(dribble[1], 0.2),
                                    color=Color(string='red'))
        end_time = time.time()
        if end_time - start_time > max_dribble_time:
            max_dribble_time = end_time - start_time
        log.sw_log().dribble().add_text( 'time:{} max is {}'.format(end_time - start_time, max_dribble_time))
        return self.candidates

    def generate_simple_dribble(self, wm: 'WorldModel'):
        angle_div = 16
        angle_step = 360.0 / angle_div

        sp = SP.i()
        ptype = wm.self().player_type()

        my_first_speed = wm.self().vel().r()

        for a in range(angle_div):
            dash_angle = wm.self().body() + (angle_step * a)

            if wm.self().pos().x() < 16.0 and dash_angle.abs() > 100.0:
                if debug_dribble:
                    log.sw_log().dribble().add_text( '#dash angle:{} cancel is not safe1'.format(dash_angle))
                continue

            if wm.self().pos().x() < -36.0 and wm.self().pos().abs_y() < 20.0 and dash_angle.abs() > 45.0:
                if debug_dribble:
                    log.sw_log().dribble().add_text( '#dash angle:{} cancel is not safe2'.format(dash_angle))
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
                if debug_dribble:
                    log.sw_log().dribble().add_text( '#dash angle:{} turn:{}'.format(dash_angle, n_turn))
            self.simulate_kick_turns_dashes(wm, dash_angle, n_turn)

    def simulate_kick_turns_dashes(self, wm: 'WorldModel', dash_angle, n_turn):
        max_dash = 8
        min_dash = 2

        self_cache = []

        self.create_self_cache(wm, dash_angle, n_turn, max_dash, self_cache)
        if debug_dribble:
            log.sw_log().dribble().add_text( '##self_cache:{}'.format(self_cache))
        sp = SP.i()
        ptype = wm.self().player_type()

        # trap_rel = Vector2D.polar2vector(ptype.playerSize() + ptype.kickableMargin() * 0.2 + SP.ball_size(), dash_angle)
        trap_rel = Vector2D.polar2vector(ptype.player_size() + ptype.kickable_margin() * 0.2 + 0, dash_angle)

        max_x = sp.pitch_half_length() - 1.0
        max_y = sp.pitch_half_width() - 1.0

        for n_dash in range(max_dash, min_dash - 1, -1):
            self.index += 1
            ball_trap_pos:Vector2D = self_cache[n_turn + n_dash] + trap_rel

            if ball_trap_pos.abs_x() > max_x or ball_trap_pos.abs_y() > max_y:
                if debug_dribble:
                    log.sw_log().dribble().add_text(
                                  '#index:{} target:{} our of field'.format(self.index, ball_trap_pos))
                    self.debug_list.append((self.index, ball_trap_pos, False))
                continue

            term = (1.0 - pow(sp.ball_decay(), 1 + n_turn + n_dash ) ) / (1.0 - sp.ball_decay())
            first_vel: Vector2D = (ball_trap_pos - wm.ball().pos()) / term
            kick_accel: Vector2D = first_vel - wm.ball().vel()
            kick_power = kick_accel.r() / wm.self().kick_rate()

            if kick_power > sp.max_power() or kick_accel.r2() > pow(sp.ball_accel_max(), 2) or first_vel.r2() > pow(
                    sp.ball_speed_max(), 2):
                if debug_dribble:
                    log.sw_log().dribble().add_text(
                                  '#index:{} target:{} need more power, power:{}, accel:{}, vel:{}'.format(
                                      self.index, ball_trap_pos, kick_power, kick_accel, first_vel))
                    self.debug_list.append((self.index, ball_trap_pos, False))
                continue

            if (wm.ball().pos() + first_vel).dist2(self_cache[0]) < pow(ptype.player_size() + sp.ball_size() + 0.1, 2):
                if debug_dribble:
                    log.sw_log().dribble().add_text(
                                  '#index:{} target:{} in body, power:{}, accel:{}, vel:{}'.format(
                                      self.index, ball_trap_pos, kick_power, kick_accel, first_vel))
                self.debug_list.append((self.index, ball_trap_pos, False))
                continue

            if self.check_opponent(wm, ball_trap_pos, 1 + n_turn + n_dash):
                candidate = KickAction()
                candidate.type = KickActionType.Dribble
                candidate.start_ball_pos = wm.ball().pos()
                candidate.target_ball_pos = ball_trap_pos
                candidate.target_unum = wm.self().unum()
                candidate.start_ball_speed = first_vel.r()
                candidate.index = self.index
                candidate.evaluate(wm)
                self.candidates.append(candidate)
                if debug_dribble:
                    log.sw_log().dribble().add_text(
                                  '#index:{} target:{}, power:{}, accel:{}, vel:{} OK'.format(
                                      self.index, ball_trap_pos, kick_power, kick_accel, first_vel))
                    self.debug_list.append((self.index, ball_trap_pos, True))
            else:
                if debug_dribble:
                    log.sw_log().dribble().add_text(
                                  '#index:{} target:{}, power:{}, accel:{}, vel:{} Opponent catch it'.format(
                                      self.index, ball_trap_pos, kick_power, kick_accel, first_vel))
                    self.debug_list.append((self.index, ball_trap_pos, False))

    def create_self_cache(self, wm: 'WorldModel', dash_angle, n_turn, n_dash, self_cache):
        sp = SP.i()
        ptype = wm.self().player_type()

        self_cache.clear()

        stamina_model = wm.self().stamina_model()

        my_pos = wm.self().pos()
        my_vel = wm.self().vel()

        my_pos += my_vel
        my_vel *= ptype.player_decay()

        self_cache.append(Vector2D(my_pos))

        for i in range(n_turn):
            my_pos += my_vel
            my_vel *= ptype.player_decay()
            self_cache.append(Vector2D(my_pos))
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
                self_cache.append(Vector2D(my_pos))

    def check_opponent(self, wm: 'WorldModel', ball_trap_pos: Vector2D, dribble_step: int):
        sp = SP.i()
        ball_move_angle:AngleDeg = (ball_trap_pos - wm.ball().pos()).th()

        for o in range(12):
            opp: 'PlayerObject' = wm.their_player(o)
            if opp is None or opp.unum() == 0:
                if debug_dribble:
                    log.sw_log().dribble().add_text( "###OPP {} is ghost".format(o))
                continue

            if opp.dist_from_self() > 20.0:
                if debug_dribble:
                    log.sw_log().dribble().add_text( "###OPP {} is far".format(o))
                continue

            ptype = opp.player_type()

            control_area = (sp._catchable_area
                            if opp.goalie()
                               and ball_trap_pos.x() > sp.their_penalty_area_line_x()
                               and ball_trap_pos.abs_y() < sp.penalty_area_half_width()
                            else ptype.kickable_area())

            opp_pos = opp.inertia_point( dribble_step )

            ball_to_opp_rel = (opp.pos() - wm.ball().pos()).rotated_vector(-ball_move_angle)

            if ball_to_opp_rel.x() < -4.0:
                if debug_dribble:
                    log.sw_log().dribble().add_text( "###OPP {} is behind".format(o))
                continue

            target_dist = opp_pos.dist(ball_trap_pos)

            if target_dist - control_area < 0.001:
                if debug_dribble:
                    log.sw_log().dribble().add_text( "###OPP {} Catch, ball will be in his body".format(o))
                return False

            dash_dist = target_dist
            dash_dist -= control_area * 0.5
            dash_dist -= 0.2
            n_dash = ptype.cycles_to_reach_distance(dash_dist)

            n_turn = 1 if opp.body_count() > 1 else Tools.predict_player_turn_cycle(ptype,
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
                bonus_step += smath.bound(0, opp.pos_count(), 8)
            else:
                bonus_step += smath.bound(0, opp.pos_count(), 4)

            if n_step - bonus_step <= dribble_step:
                if debug_dribble:
                    log.sw_log().dribble().add_text(
                                  "###OPP {} catch n_step:{}, dr_step:{}, bonas:{}".format(o, n_step, dribble_step,
                                                                                       bonus_step))
                return False
            else:
                if debug_dribble:
                    log.sw_log().dribble().add_text(
                                  "###OPP {} can't catch n_step:{}, dr_step:{}, bonas:{}".format(o, n_step, dribble_step,
                                                                                           bonus_step))
        return True

