from math import ceil
from lib.action.intercept_info import InterceptInfo
from lib.debug.debug import log
from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.line_2d import Line2D
from pyrusgeom.segment_2d import Segment2D
from pyrusgeom.soccer_math import bound, calc_first_term_geom_series, min_max
from pyrusgeom.vector_2d import Vector2D
from lib.player.object_ball import BallObject
from lib.player.object_player import PlayerObject
from lib.player.stamina_model import StaminaModel
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.player.world_model import WorldModel

control_area_buf = 0.15

DEBUG = True


class SelfIntercept:
    def __init__(self, wm, ball_cache):
        self._wm: 'WorldModel' = wm
        self._ball_cache = ball_cache

        self._max_short_step = 5
        self._min_turn_thr = 12.5
        self._back_dash_thr_angle = 100

    def predict(self, max_cycle, self_cache: list):
        if len(self._ball_cache) < 2:
            log.sw_log().intercept().add_text("no ball position cache :(")
            return

        save_recovery: bool = self._wm.self().stamina_model().capacity() != 0

        self.predict_one_step(self_cache)
        self.predict_short_step(max_cycle, save_recovery, self_cache)
        self.predict_long_step(max_cycle, save_recovery, self_cache)

        self_cache.sort()  # TODO check this
        log.sw_log().intercept().add_text("self pred all sorted intercept")
        for ii in self_cache:
            log.sw_log().intercept().add_text(f"{ii}")

    def predict_one_step(self, self_cache):
        wm = self._wm
        ball_next: Vector2D = wm.ball().pos() + wm.ball().vel()
        goalie_mode: bool = self.is_goalie_mode(ball_next)
        control_area: float = wm.self().player_type().catchable_area() if \
            goalie_mode else \
            wm.self().player_type().kickable_area()

        # dist is to far never reach with one dash
        if wm.ball().dist_from_self() > \
                ServerParam.i().ball_speed_max() \
                + wm.self().player_type().real_speed_max() \
                + control_area:
            return
        if self.predict_no_dash(self_cache):
            return
        self.predict_one_dash(self_cache)

    def predict_no_dash(self, self_cache) -> bool:
        log.sw_log().intercept().add_text("=================== predict_no_dash ======================")
        SP = ServerParam.i()
        wm: 'WorldModel' = self._wm
        me: PlayerObject = wm.self()

        my_next: Vector2D = me.pos() + me.vel()
        ball_next: Vector2D = wm.ball().pos() + wm.ball().vel()
        goalie_mode: bool = self.is_goalie_mode(ball_next)
        control_area: float = me.player_type().catchable_area() if \
            goalie_mode else \
            me.player_type().kickable_area()
        next_ball_rel: Vector2D = (ball_next - my_next).rotated_vector(-me.body())
        ball_noise: float = wm.ball().vel().r() * SP.ball_rand()
        next_ball_dist: float = next_ball_rel.r()

        # out of control area
        if next_ball_dist > control_area - 0.15 - ball_noise:
            log.sw_log().intercept().add_text("----->>>> NO ball is out of intercept no dash area")
            return False

        # if goalie immediately success
        if goalie_mode:
            stamina_model: StaminaModel = me.stamina_model()
            stamina_model.simulate_wait(me.player_type())

            self_cache.append(InterceptInfo(InterceptInfo.Mode.NORMAL,
                                            1, 0,
                                            0, 0,
                                            my_next,
                                            next_ball_dist,
                                            stamina_model.stamina()))
            log.sw_log().intercept().add_text("------>>>>> OK goal mode success")
            return True

        # check kick effectiveness
        ptype: PlayerType = me.player_type()
        if next_ball_dist > ptype.player_size() + SP.ball_size():
            kick_rate: float = ptype.kick_rate(next_ball_dist,
                                               next_ball_rel.th().degree())
            next_ball_vel: Vector2D = wm.ball().vel() * SP.ball_decay()
            if SP.max_power() * kick_rate <= next_ball_vel.r() * SP.ball_decay() * 1.1:
                log.sw_log().intercept().add_text("------>>>>> NO can not control the ball")
                return False

        # at least, player can stop the ball
        stamina_model = me.stamina_model()
        self_cache.append(InterceptInfo(InterceptInfo.Mode.NORMAL,
                                        1, 0,  # 1 turn
                                        0, 0,
                                        my_next,
                                        next_ball_dist,
                                        stamina_model.stamina()))
        log.sw_log().intercept().add_text("----->>>>> OK can control with out dash")
        return True

    def is_goalie_mode(self, ball_next, x_limit=None, abs_y_limit=None) -> bool:
        wm = self._wm
        if x_limit is None:
            x_limit = ServerParam.i().our_penalty_area_line_x()
        if abs_y_limit is None:
            abs_y_limit = ServerParam.i().penalty_area_half_width()

        return (wm.self().goalie() and
                wm.last_kicker_side() != wm.our_side() and
                ball_next.x() < x_limit and
                ball_next.abs_y() < abs_y_limit)

    def predict_one_dash(self, self_cache):
        log.sw_log().intercept().add_text("=================== predict_one_dash ======================")
        tmp_cache = []

        SP = ServerParam.i()
        wm: 'WorldModel' = self._wm
        ball: BallObject = wm.ball()
        me: PlayerObject = wm.self()
        ptype: PlayerType = me.player_type()

        ball_next: Vector2D = ball.pos() + ball.vel()
        goalie_mode: bool = self.is_goalie_mode(ball_next)
        control_area: float = ptype.catchable_area() if \
            goalie_mode else \
            ptype.kickable_area()
        dash_angle_step: float = max(5, SP.dash_angle_step())
        min_dash_angle = (SP.min_dash_angle()
                          if -180 < SP.min_dash_angle() and SP.max_dash_angle() < 180
                          else dash_angle_step * int(-180 / dash_angle_step))
        max_dash_angle = (SP.max_dash_angle() + dash_angle_step * 0.5
                          if -180 < SP.min_dash_angle() and SP.max_dash_angle() < 180
                          else dash_angle_step * int(180 / dash_angle_step) - 1)

        n_steps = int((max_dash_angle - min_dash_angle) / dash_angle_step)
        dirs = [min_dash_angle + d * dash_angle_step for d in range(n_steps)]
        for dash_dir in dirs:
            dash_angle: AngleDeg = me.body() + SP.discretize_dash_angle(SP.normalize_dash_angle(dash_dir))
            dash_rate: float = me.dash_rate() * SP.dash_dir_rate(dash_dir)
            log.sw_log().intercept().add_text(f"----- dash dir={dash_dir}, angle={dash_angle}, dash_rate={dash_rate}")

            # check recovery save dash
            forward_dash_power = bound(0,
                                       me.stamina() - SP.recover_dec_thr_value() - 1,
                                       SP.max_dash_power())
            back_dash_power = bound(SP.min_dash_power(),
                                    (me.stamina() - SP.recover_dec_thr_value() - 1) * -0.5,
                                    0)

            max_forward_accel = Vector2D.polar2vector(forward_dash_power * dash_rate,
                                                      dash_angle)
            max_back_accel = Vector2D.polar2vector(back_dash_power * dash_rate,
                                                   dash_angle)
            ptype.normalize_accel(me.vel(), max_forward_accel)
            ptype.normalize_accel(me.vel(), max_back_accel)

            info: InterceptInfo = InterceptInfo()
            if self.predict_one_dash_adjust(dash_angle,
                                            max_forward_accel,
                                            max_back_accel,
                                            control_area,
                                            info):
                log.sw_log().intercept().add_text("---->>>> OK Register 1 dash intercept(1)")
                tmp_cache.append(info)
                continue

            # check max_power_dash
            if abs(forward_dash_power - SP.max_dash_power()) < 1 and \
                    abs(back_dash_power - SP.min_dash_power()) < 1:
                log.sw_log().intercept().add_text("---->>>> NO max dash power")
                continue

            max_forward_accel = Vector2D.polar2vector(SP.max_dash_power() * dash_rate,
                                                      dash_angle)
            max_back_accel = Vector2D.polar2vector(SP.min_dash_power() * dash_rate,
                                                   dash_angle)
            ptype.normalize_accel(me.vel(), max_forward_accel)
            ptype.normalize_accel(me.vel(), max_back_accel)

            info: InterceptInfo = InterceptInfo()
            if self.predict_one_dash_adjust(dash_angle,
                                            max_forward_accel,
                                            max_back_accel,
                                            control_area,
                                            info):
                log.sw_log().intercept().add_text("---->>>> OK Register 1 dash intercept(2)")
                tmp_cache.append(info)
                continue

        if len(tmp_cache) == 0:
            log.sw_log().intercept().add_text("======>>>>> No one dash intercept")
            return
        best: InterceptInfo = tmp_cache[0]
        for it in tmp_cache:
            if best.ball_dist() > it.ball_dist() or \
                    (abs(best.ball_dist() - it.ball_dist()) < 0.001 and
                     best.stamina() < it.stamina()):
                best = it
        log.sw_log().intercept().add_text(f'=====>>>> best one dash: {str(best)}')
        self_cache.append(best)

    def predict_one_dash_adjust(self,
                                dash_angle: AngleDeg,
                                max_forward_accel: Vector2D,
                                max_back_accel: Vector2D,
                                control_area: float,
                                info: InterceptInfo):
        SP = ServerParam.i()
        wm = self._wm
        me = wm.self()

        control_buf = control_area - 0.075
        dash_dir: AngleDeg = dash_angle - me.body()
        ball_next = wm.ball().pos() + wm.ball().vel()
        me_next = me.pos() + me.vel()

        ball_rel: Vector2D = (ball_next - me_next).rotated_vector(-dash_angle)
        forward_accel_rel: Vector2D = max_forward_accel.rotated_vector(-dash_angle)
        back_accel_rel: Vector2D = max_back_accel.rotated_vector(-dash_angle)
        dash_rate = me.dash_rate() * SP.dash_dir_rate(dash_dir.degree())
        # debug_print(
        # f"self pred one dash adjust dir={dash_dir}, ball_rel={ball_rel} ,_____ max_forward_accel={max_forward_accel} rel={forward_accel_rel} , _____ max_back_accel={max_back_accel} rel={back_accel_rel}")
        log.sw_log().intercept().add_text(
            f"self pred one dash adjust dir={dash_dir}, ball_rel={ball_rel}")
        log.sw_log().intercept().add_text(
            f"_____ max_forward_accel={max_forward_accel} rel={forward_accel_rel}")
        log.sw_log().intercept().add_text(
            f"_____ max_back_accel={max_back_accel} rel={back_accel_rel}")

        if ball_rel.abs_y() > control_buf or \
                Segment2D(forward_accel_rel, back_accel_rel).dist(ball_rel) > control_buf:
            return False

        dash_power = -1000

        # small x difference
        # player can put the ball on his side
        if back_accel_rel.x() < ball_rel.x() < forward_accel_rel.x():
            dash_power = self.get_one_step_dash_power(ball_rel,
                                                      dash_angle,
                                                      forward_accel_rel.x(),
                                                      back_accel_rel.x())
            log.sw_log().intercept().add_text(
                f"self pred one dash adjust (1). dash_power={dash_power}")

        # big x difference x (>0)
        if dash_power < -999 and \
                forward_accel_rel.x() < ball_rel.x():
            enable_ball_dist = ball_rel.dist(forward_accel_rel)
            if enable_ball_dist < control_buf:
                dash_power = forward_accel_rel.x() / dash_rate
                log.sw_log().intercept().add_text(
                    f"self pred one dash adjust (2). not best." +
                    f"next_ball_dist={enable_ball_dist}, dash_power={dash_power}")

        # big x difference (<0)
        if dash_power < -999 and \
                ball_rel.x() < back_accel_rel.x():
            enable_ball_dist = ball_rel.dist(back_accel_rel)
            if enable_ball_dist < control_buf:
                dash_power = back_accel_rel.x() / dash_rate
                log.sw_log().intercept().add_text(
                    f"self pred one dash adjust (3). not best." +
                    f"next_ball_dist={enable_ball_dist}, dash_power={dash_power}")

        # check if adjustable
        if dash_power < -999 and \
                back_accel_rel.x() < ball_rel.x() < forward_accel_rel.x():
            dash_power = ball_rel.x() / dash_rate
            log.sw_log().intercept().add_text(
                f"self pred one dash adjust (4). not best." +
                f"just adjust X. dash_power={dash_power}")

        # register
        if dash_power < -999:
            log.sw_log().intercept().add_text("self pred one dash adjust XXX FAILED")
            return False

        mode = InterceptInfo.Mode.NORMAL
        accel = Vector2D.polar2vector(dash_power * dash_rate, dash_angle)
        my_vel = me.vel() + accel
        my_pos = me.pos() + my_vel

        stamina_model = me.stamina_model()
        stamina_model.simulate_dash(me.player_type(), dash_power)

        if stamina_model.stamina() < SP.recover_dec_thr_value() and \
                not stamina_model.capacity_is_empty():
            mode = InterceptInfo.Mode.EXHAUST

        info.init(mode, 0, 1, dash_power, dash_dir.degree(),
                  my_pos,
                  my_pos.dist(ball_next),
                  stamina_model.stamina())
        log.sw_log().intercept().add_text(
            f"self pred one dash adjust Success! "
            f"power={info.dash_power()}, "
            f"rel_dir={info.dash_angle()}, "
            f"angle={dash_angle.degree()}"
            f"my_pos={my_pos}"
            f"ball_dist={info.ball_dist()}"
            f"stamina={stamina_model.stamina()}")
        return True

    def get_one_step_dash_power(self,
                                next_ball_rel: Vector2D,
                                dash_angle: AngleDeg,
                                max_forward_accel_x: float,
                                max_back_accel_x):
        wm = self._wm

        dash_rate = wm.self().dash_rate() * ServerParam.i().dash_dir_rate(dash_angle.degree())
        ptype = wm.self().player_type()
        best_ctrl_dist_forward = (ptype.player_size()
                                  + ptype.kickable_margin() / 2
                                  + ServerParam.i().ball_size())
        best_ctrl_dist_backward = (ptype.player_size()
                                   + 0.3 * ptype.kickable_margin()
                                   + ServerParam.i().ball_size())

        # y diff is longer than best dist.
        # just put the ball on player's side
        if next_ball_rel.abs_y() > best_ctrl_dist_forward:  # TODO FIX COMPLEX
            return next_ball_rel.x() / dash_rate
        # if next_ball_rel.y()**2 > best_ctrl_dist_forward**2:
        #     return next_ball_rel.x() / dash_rate
        forward_trap_accel_x = (next_ball_rel.x()
                                - (best_ctrl_dist_forward ** 2
                                   - next_ball_rel.y() ** 2) ** 0.5)
        backward_trap_accel_x = (next_ball_rel.x()
                                 + (best_ctrl_dist_backward ** 2
                                    - next_ball_rel.y() ** 2) ** 0.5)

        best_accel_x = 10000
        min_power = 10000

        x_step = (backward_trap_accel_x - forward_trap_accel_x) / 5
        # debug_print("forward_trap_accel_x:", forward_trap_accel_x, "| backward_trap_accel_x :", backward_trap_accel_x,
        #       "| X_step :",
        #       x_step)
        accels = [forward_trap_accel_x + a * x_step for a in range(5)]
        for accel_x in accels:
            if (0 <= accel_x < max_forward_accel_x) or \
                    (max_back_accel_x < accel_x < 0):
                power = accel_x / dash_rate
                if abs(power) < abs(min_power):
                    best_accel_x = accel_x
                    min_power = power

        if min_power < 1000:
            return min_power
        return -1000

    def predict_short_step(self, max_cycle, save_recovery, self_cache):
        tmp_cache = []
        max_loop = min(self._max_short_step, max_cycle)

        SP = ServerParam.i()
        wm = self._wm
        ball = wm.ball()
        me = wm.self()
        ptype = me.player_type()

        pen_area_x = SP.our_penalty_area_line_x() - 0.5
        pen_area_y = SP.penalty_area_half_width() - 0.5

        ball_to_self = (me.pos() - ball.pos()).rotated_vector(-ball.vel().th())
        min_cycle = int(ceil((ball_to_self.abs_y() - ptype.kickable_area())
                             / ptype.real_speed_max()))

        if min_cycle >= max_loop:
            return
        if min_cycle < 2:
            min_cycle = 2

        ball_pos = ball.inertia_point(min_cycle - 1)
        ball_vel = ball.vel() * SP.ball_decay() ** (min_cycle - 1)

        for cycle in range(min_cycle, max_loop + 1):
            tmp_cache = []
            ball_pos += ball_vel
            ball_vel *= SP.ball_decay()
            log.sw_log().intercept().add_text(f"self pred short cycle {cycle}: bpos={ball_pos}, bvel={ball_vel}")

            goalie_mode = self.is_goalie_mode(ball_pos, pen_area_x, pen_area_y)
            control_area = (ptype.catchable_area()
                            if goalie_mode
                            else ptype.kickable_area())
            if (control_area + ptype.real_speed_max() * cycle) ** 2 < me.pos().dist2(ball_pos):
                log.sw_log().intercept().add_text("self pred short too far")
                continue

            self.predict_turn_dash_short(cycle, ball_pos, control_area, save_recovery,  # forward dash
                                         False,
                                         max(0.1, control_area - 0.4),
                                         tmp_cache)

            self.predict_turn_dash_short(cycle, ball_pos, control_area, save_recovery,  # forward dash
                                         False,
                                         max(0.1, control_area - control_area_buf),
                                         tmp_cache)

            self.predict_turn_dash_short(cycle, ball_pos, control_area, save_recovery,  # back dash
                                         True,
                                         max(0.1, control_area - 0.4),
                                         tmp_cache)

            self.predict_turn_dash_short(cycle, ball_pos, control_area, save_recovery,  # back dash
                                         True,
                                         control_area - control_area_buf,
                                         tmp_cache)

            if cycle <= 2:
                self.predict_omni_dash_short(cycle, ball_pos, control_area, save_recovery,
                                             False, tmp_cache)

            if len(tmp_cache) == 0:
                continue

            safety_ball_dist = max(control_area - 0.2 - ball.pos().dist(ball_pos) * SP.ball_rand(),
                                   ptype.player_size() + SP.ball_size() + ptype.kickable_margin() * 0.4)
            best: InterceptInfo = tmp_cache[0]
            for it in tmp_cache[1:]:
                if best.ball_dist() < safety_ball_dist and \
                        it.ball_dist() < safety_ball_dist:
                    if best.turn_cycle() > it.turn_cycle():
                        best = it
                    elif best.turn_cycle() == it.turn_cycle() and \
                            best.stamina() < it.stamina():
                        best = it
                else:
                    if best.turn_cycle() >= it.turn_cycle() and \
                            (best.ball_dist() > it.ball_dist()
                             or (abs(best.ball_dist() - it.ball_dist()) < 0.001
                                 and best.stamina() < it.stamina())):
                        best = it
            self_cache.append(best)

    def predict_omni_dash_short(self,
                                cycle: int,
                                ball_pos: Vector2D,
                                control_area: float,
                                save_recovery: bool,
                                back_dash: bool,
                                self_cache: list):
        SP = ServerParam.i()
        wm = self._wm

        me = wm.self()
        ptype = me.player_type()

        body_angle = me.body() + 180 if back_dash else me.body()
        my_inertia = me.inertia_point(cycle)
        target_line = Line2D(p=ball_pos, a=body_angle)

        if target_line.dist(my_inertia) < control_area - 0.4:
            return

        recover_dec_thr = SP.recover_dec_thr_value() + 1
        dash_angle_step = max(15, SP.dash_angle_step())
        min_dash_angle = (SP.min_dash_angle()
                          if -180 < SP.min_dash_angle() and SP.max_dash_angle() < 180
                          else dash_angle_step * int(-180 / dash_angle_step))
        max_dash_angle = (SP.max_dash_angle() + dash_angle_step * 0.5
                          if -180 < SP.min_dash_angle() and SP.max_dash_angle() < 180
                          else dash_angle_step * int(180 / dash_angle_step) - 1)

        target_angle = (ball_pos - my_inertia).th()

        n_steps = int((max_dash_angle - min_dash_angle) / dash_angle_step)
        dirs = [min_dash_angle + d * dash_angle_step for d in range(n_steps)]
        for dirr in dirs:
            if abs(dirr) < 1:
                continue

            dash_angle = body_angle + SP.discretize_dash_angle(SP.normalize_dash_angle(dirr))
            if (dash_angle - target_angle).abs() > 91:
                continue

            first_dash_power = 0
            my_pos = me.pos()
            my_vel = me.vel()
            stamina_model = me.stamina_model()

            n_omni_dash, first_dash_power = self.predict_adjust_omni_dash(cycle,
                                                                          ball_pos,
                                                                          control_area,
                                                                          save_recovery,
                                                                          back_dash,
                                                                          dirr,
                                                                          my_pos,
                                                                          my_vel,
                                                                          stamina_model,
                                                                          first_dash_power)
            if n_omni_dash < 0:
                continue
            if n_omni_dash == 0:
                continue

            # check target point direction
            inertia_pos = ptype.inertia_point(my_pos, my_vel, cycle - n_omni_dash)
            target_rel = (ball_pos - inertia_pos).rotated_vector(-body_angle)

            if ((back_dash and target_rel.x() > 0) or
                    (not back_dash and target_rel.x() < 0)):
                continue

            # dash to the body direction
            body_accel_unit = Vector2D.polar2vector(1, body_angle)
            for n_dash in range(n_omni_dash + 1, cycle + 1):
                first_speed = calc_first_term_geom_series((ball_pos - my_pos).rotated_vector(-body_angle).x(),
                                                          ptype.player_decay(),
                                                          cycle - n_dash + 1)
                rel_vel = my_vel.rotated_vector(-body_angle)
                required_accel = first_speed - rel_vel.x()
                dash_power = required_accel / (ptype.dash_rate(stamina_model.effort()))
                if back_dash:
                    dash_power = -dash_power

                available_stamina = (max(0, stamina_model.stamina() - recover_dec_thr)
                                     if save_recovery
                                     else stamina_model.stamina() + ptype.extra_stamina())

                if back_dash:
                    dash_power = bound(SP.min_dash_power(), dash_power, 0)
                    dash_power = max(dash_power, available_stamina * -0.5)
                else:
                    dash_power = bound(0, dash_power, SP.max_dash_power())
                    dash_power = min(available_stamina, dash_power)

                accel_mag = abs(dash_power) * ptype.dash_rate(stamina_model.effort())
                accel = body_accel_unit * accel_mag

                my_vel += accel
                my_pos += my_vel
                my_vel *= ptype.player_decay()
                stamina_model.simulate_dash(ptype, dash_power)

            my_move = my_pos - me.pos()
            if my_pos.dist2(ball_pos) < (control_area - control_area_buf) ** 2 or \
                    my_move.r() > (ball_pos - me.pos()).rotated_vector(-my_move.th()).abs_x():
                mode = (InterceptInfo.Mode.EXHAUST
                        if stamina_model.recovery() < me.stamina_model().recovery()
                           and not stamina_model.capacity_is_empty()
                        else InterceptInfo.Mode.NORMAL)
                self_cache.append(InterceptInfo(mode,
                                                0, cycle,
                                                first_dash_power, dirr,
                                                my_pos,
                                                my_pos.dist(ball_pos),
                                                stamina_model.stamina()))

    def predict_adjust_omni_dash(self,
                                 cycle: int,
                                 ball_pos: Vector2D,
                                 control_area: float,
                                 save_recovery: bool,
                                 back_dash: bool,
                                 dash_rel_dir: float,
                                 my_pos: Vector2D,
                                 my_vel: Vector2D,
                                 stamina_model: StaminaModel,
                                 first_dash_power) -> tuple:
        SP = ServerParam.i()
        wm = self._wm
        me = wm.self()
        ptype = me.player_type()

        recover_dec_thr = SP.recover_dec_thr_value() + 1
        max_omni_dash = min(2, cycle)

        body_angle = me.body() + 180 if back_dash else me.body()
        target_line = Line2D(p=ball_pos, a=body_angle)
        my_inertia = me.inertia_point(cycle)

        if target_line.dist(my_inertia) < control_area - 0.4:
            first_dash_power = 0
            return 0, first_dash_power

        dash_angle = body_angle + SP.discretize_dash_angle(SP.normalize_dash_angle(dash_rel_dir))
        accel_unit = Vector2D.polar2vector(1, dash_angle)
        dash_dir_rate = SP.dash_dir_rate(dash_rel_dir)

        # dash simulation
        for n_omni_dash in range(1, max_omni_dash + 1):
            first_speed = calc_first_term_geom_series(max(0, target_line.dist(my_pos)),
                                                      ptype.player_decay(),
                                                      cycle - n_omni_dash + 1)
            rel_vel = my_vel.rotated_vector(-dash_angle)
            required_accel = first_speed - rel_vel.x()

            if abs(required_accel) < 0.01:
                return n_omni_dash - 1, first_dash_power

            dash_power = required_accel / (ptype.dash_rate(stamina_model.effort())
                                           * dash_dir_rate)
            available_stamina = (max(0, stamina_model.stamina() - recover_dec_thr)
                                 if save_recovery
                                 else stamina_model.stamina() + ptype.extra_stamina())
            if back_dash:
                dash_power = bound(SP.min_dash_power(), dash_power, 0)
                dash_power = max(dash_power, available_stamina * -0.5)
            else:
                dash_power = bound(0, dash_power, SP.max_dash_power())
                dash_power = min(available_stamina, dash_power)

            if n_omni_dash == 1:
                first_dash_power = dash_power

            accel_mag = (abs(dash_power)
                         * ptype.dash_rate(stamina_model.effort())
                         * dash_dir_rate)
            accel = accel_unit * accel_mag
            my_vel += accel
            my_pos += my_vel
            my_vel *= ptype.player_decay()

            stamina_model.simulate_dash(ptype, dash_power)
            inertia_pos = ptype.inertia_point(my_pos, my_vel, cycle - n_omni_dash)

            if target_line.dist(inertia_pos) < control_area - control_area_buf:
                return n_omni_dash, first_dash_power
        return -1, first_dash_power

    def predict_turn_dash_short(self,
                                cycle: int,
                                ball_pos: Vector2D,
                                control_area: float,
                                save_recovery: bool,
                                back_dash: bool,
                                turn_margin_control_area: float,
                                self_cache: list):
        dash_angle = self._wm.self().body()
        n_turn = self.predict_turn_cycle_short(cycle, ball_pos, control_area, back_dash,
                                               turn_margin_control_area,
                                               dash_angle)
        if n_turn > cycle:
            return

        self.predict_dash_cycle_short(cycle, n_turn, ball_pos, dash_angle,
                                      control_area, save_recovery, back_dash,
                                      self_cache)

    def predict_dash_cycle_short(self,
                                 cycle: int,
                                 n_turn: int,
                                 ball_pos: Vector2D,
                                 dash_angle: AngleDeg,
                                 control_area: float,
                                 save_recovery: bool,
                                 back_dash: bool,
                                 self_cache):
        SP = ServerParam.i()
        wm = self._wm

        me = wm.self()
        ptype = me.player_type()

        recover_dec_thr = SP.recover_dec_thr_value() + 1
        max_dash = cycle - n_turn

        my_inertia = me.inertia_point(cycle)
        my_pos = me.inertia_point(n_turn)
        my_vel = me.vel() * ptype.player_decay() ** n_turn

        stamina_model = me.stamina_model()
        stamina_model.simulate_waits(ptype, n_turn)

        if my_inertia.dist2(ball_pos) < (control_area - control_area_buf) ** 2:
            my_final_pos = my_inertia.copy()
            tmp_stamina = stamina_model.copy()
            tmp_stamina.simulate_waits(ptype, cycle - n_turn)
            self_cache.append(InterceptInfo(InterceptInfo.Mode.NORMAL,
                                            n_turn, cycle - n_turn,
                                            0, 0,
                                            my_final_pos,
                                            my_final_pos.dist(ball_pos),
                                            tmp_stamina.stamina()))

        target_angle: AngleDeg = (ball_pos - my_inertia).th()
        if (target_angle - dash_angle).abs() > 90:
            log.sw_log().intercept().add_text(
                "self pred short target_angle - dash_angle > 90")
            return

        accel_unit = Vector2D.polar2vector(1, dash_angle)
        first_dash_power = 0
        for n_dash in range(1, max_dash + 1):
            log.sw_log().intercept().add_text(
                f"self pred short dash {n_dash}: max_dash={max_dash}")
            ball_rel = (ball_pos - my_pos).rotated_vector(-dash_angle)
            first_speed = calc_first_term_geom_series(ball_rel.x(),
                                                      ptype.player_decay(),
                                                      max_dash - n_dash + 1)
            rel_vel = my_vel.rotated_vector(-dash_angle)
            required_accel = first_speed - rel_vel.x()
            dash_power = required_accel / ptype.dash_rate(stamina_model.effort())
            if back_dash:
                dash_power = -dash_power

            available_stamina = (max(0, stamina_model.stamina() - recover_dec_thr)
                                 if save_recovery
                                 else stamina_model.stamina() + ptype.extra_stamina())
            if back_dash:
                dash_power = bound(SP.min_dash_power(), dash_power, 0)
                dash_power = max(dash_power, available_stamina * -0.5)
            else:
                dash_power = bound(0, dash_power, SP.max_dash_power())
                dash_power = min(available_stamina, dash_power)

            if n_dash == 1:
                first_dash_power = dash_power

            accel_mag = abs(dash_power * ptype.dash_rate(stamina_model.effort()))
            accel: Vector2D = accel_unit * accel_mag

            my_vel += accel
            my_pos += my_vel
            my_vel *= ptype.player_decay()

            stamina_model.simulate_dash(ptype, dash_power)

        if my_pos.dist2(ball_pos) < (control_area - control_area_buf) ** 2 or \
                me.pos().dist2(my_pos) > me.pos().dist2(ball_pos):
            mode = (InterceptInfo.Mode.EXHAUST
                    if stamina_model.stamina() < SP.recover_dec_thr_value()
                       and not stamina_model.capacity_is_empty()
                    else InterceptInfo.Mode.NORMAL)

            self_cache.append(InterceptInfo(mode, n_turn, cycle - n_turn,
                                            first_dash_power, 180 if back_dash else 0,
                                            my_pos,
                                            my_pos.dist(ball_pos),
                                            stamina_model.stamina()))

    def predict_turn_cycle_short(self,
                                 cycle: int,
                                 ball_pos: Vector2D,
                                 _: float,
                                 back_dash: bool,
                                 turn_margin_control_area: float,
                                 result_dash_angle: AngleDeg) -> int:
        SP = ServerParam.i()
        wm = self._wm
        max_moment = SP.max_moment()

        me = wm.self()
        ptype = me.player_type()

        dist_thr = turn_margin_control_area
        inertia_pos = me.inertia_point(cycle)
        target_dist = (ball_pos - inertia_pos).r()
        target_angle = (ball_pos - inertia_pos).th()

        n_turn = 0
        body_angle = me.body() + 180 if back_dash else me.body()
        angle_diff = (target_angle - body_angle).abs()

        turn_margin = 180
        if dist_thr < target_dist:
            turn_margin = max(self._min_turn_thr,
                              AngleDeg.asin_deg(dist_thr / target_dist))
        if angle_diff > turn_margin:
            my_speed = me.vel().r()
            while angle_diff > turn_margin:
                angle_diff -= ptype.effective_turn(max_moment, my_speed)
                my_speed *= ptype.player_decay()
                n_turn += 1

        result_dash_angle.set_degree(body_angle.degree())
        if n_turn > 0:
            angle_diff = max(0, angle_diff)
            if (target_angle - body_angle).degree() > 0:
                result_dash_angle.set_degree((target_angle - angle_diff).degree())
            else:
                result_dash_angle.set_degree((target_angle + angle_diff).degree())

        log.sw_log().intercept().add_text(
            f"self pred short cycle {cycle}: "
            f"turn={n_turn}, "
            f"turn_margin={turn_margin}"
            f"turn_momment={result_dash_angle.degree() - body_angle.degree()}"
            f"first_angle_diff={target_angle.degree() - body_angle.degree()}"
            f"final_angle={angle_diff}"
            f"dash_angle={result_dash_angle}")
        return n_turn

    def predict_long_step(self, max_cycle: int, save_recovery: bool, self_cache: list):
        if DEBUG:
            log.sw_log().intercept().add_text('=========================== Long Step =============================')
        tmp_cache = []
        SP = ServerParam.i()
        wm = self._wm
        ball = wm.ball()
        me = wm.self()
        ptype = me.player_type()

        # calc y distance from ball line
        ball_to_self = me.pos() - ball.pos()
        ball_to_self.rotate(-ball.vel().th())
        start_cycle = int(ceil((ball_to_self.abs_y()
                                - ptype.kickable_area()
                                - 0.2)
                               / ptype.real_speed_max()))
        # if start_cycle <= self._max_short_step:
        #     start_cycle = self._max_short_step + 1

        ball_pos = ball.inertia_point(start_cycle - 1)
        ball_vel = ball.vel() * SP.ball_decay() ** (start_cycle - 1)
        found = False

        max_loop = max_cycle
        tmp_cache = []
        for cycle in range(start_cycle, max_loop):
            ball_pos += ball_vel
            ball_vel *= SP.ball_decay()
            if DEBUG:
                log.sw_log().intercept().add_text(f'$$$ c: {cycle} b: {ball_pos}')
            if ball_pos.abs_x() > SP.pitch_half_length() + 10 or \
                    ball_pos.abs_y() > SP.pitch_half_width() + 10:
                log.sw_log().intercept().add_text('-------> out of field')
                log.sw_log().intercept().add_circle(cx=ball_pos.x(), cy=ball_pos.y(), r=0.3, color='r')
                break

            goalie_mode = self.is_goalie_mode(ball_pos)
            control_area = ptype.catchable_area() if goalie_mode else ptype.kickable_area()

            # reach point is to far never reach
            if control_area + ptype.real_speed_max() * cycle < me.pos().dist(ball_pos):
                log.sw_log().intercept().add_text('-------> to far never reach')
                log.sw_log().intercept().add_circle(cx=ball_pos.x(), cy=ball_pos.y(), r=0.3, color='r')
                continue

            res, n_turn, back_dash, result_recovery = self.can_reach_after_turn_long_dash(cycle,
                                                                                          ball_pos,
                                                                                          control_area,
                                                                                          save_recovery,
                                                                                          self_cache)
            if res:
                log.sw_log().intercept().add_text(f'-------> {res} turn:{n_turn} back_dash: {back_dash}')
                if not found:
                    max_loop = min(max_cycle, cycle + 10)
                found = True
                log.sw_log().intercept().add_circle(cx=ball_pos.x(), cy=ball_pos.y(), r=0.3, color='green')
            else:
                log.sw_log().intercept().add_text('-------> res not found')
                log.sw_log().intercept().add_circle(cx=ball_pos.x(), cy=ball_pos.y(), r=0.3, color='red')

        # not registered any intercept
        if not found and save_recovery:
            self.predict_final(max_cycle, self_cache)
        if len(self_cache) == 0:
            self.predict_final(max_cycle, self_cache)

    def can_reach_after_turn_long_dash(self,
                                       cycle,
                                       ball_pos,
                                       control_area,
                                       save_recovery,
                                       self_cache) -> tuple:
        dash_angle = self._wm.self().body()
        result_recovery = 0
        n_turn, dash_angle, back_dash = self.predict_turn_cycle(cycle,
                                                                ball_pos,
                                                                control_area,
                                                                dash_angle)
        if n_turn > cycle:
            return False, n_turn, back_dash, result_recovery

        res, result_recovery = self.can_reach_after_dash(n_turn, max(0, cycle - n_turn),
                                                         ball_pos, control_area,
                                                         save_recovery,
                                                         dash_angle, back_dash,
                                                         result_recovery,
                                                         self_cache)
        return res, n_turn, back_dash, result_recovery

    def predict_turn_cycle(self, cycle: int,
                           ball_pos: Vector2D,
                           control_area: float,
                           dash_angle: AngleDeg) -> tuple:
        wm = self._wm
        ptype = wm.self().player_type()

        back_dash = False
        n_turn = 0

        inertia_pos = wm.self().inertia_point(cycle)
        target_rel = ball_pos - inertia_pos
        target_angle = target_rel.th()

        angle_diff = (target_angle - dash_angle).degree()
        diff_is_positive = True if angle_diff > 0 else False
        angle_diff = abs(angle_diff)

        target_dist = target_rel.r()
        turn_margin = 180
        control_buf = control_area - 0.25
        control_buf = max(0.5, control_buf)
        if control_buf < target_dist:
            turn_margin = AngleDeg.asin_deg(control_buf / target_dist)
        turn_margin = max(turn_margin, self._min_turn_thr)

        # check back dash possibility
        if self.can_back_dash_chase(cycle, target_dist, angle_diff):
            back_dash = True
            dash_angle += 180
            angle_diff = 180 - angle_diff

        # predict turn cycles
        max_moment = ServerParam.i().max_moment() * (1 - ServerParam.i().player_rand())
        player_speed = wm.self().vel().r()
        while angle_diff > turn_margin:
            max_turnable = ptype.effective_turn(max_moment, player_speed)
            angle_diff -= max_turnable
            player_speed *= ptype.player_decay()
            n_turn += 1

        # update dash angle
        if n_turn > 0:
            angle_diff = max(0.0, angle_diff)
            dash_angle = target_angle + (angle_diff
                                         if diff_is_positive
                                         else -angle_diff)

        return n_turn, dash_angle, back_dash

    def can_back_dash_chase(self, cycle: int,
                            target_dist: float,
                            angle_diff: float):
        wm = self._wm

        if angle_diff < self._back_dash_thr_angle:
            return False

        if (not wm.self().goalie()
            or wm.last_kicker_side() == wm.our_side()) and cycle >= 5:
            return False

        if (wm.self().goalie()
                and wm.last_kicker_side() != wm.our_side()
                and cycle >= 5):
            if cycle >= 15:
                return False

            goal = Vector2D(-ServerParam.i().pitch_half_length(), 0)
            bpos = wm.ball().inertia_point(cycle)
            if goal.dist(bpos) > 21:
                return False

        # check stamina consumed by one step
        total_consume = -ServerParam.i().min_dash_power() * 2 * cycle
        total_recover = (wm.self().player_type().stamina_inc_max()
                         * wm.self().recovery()
                         * (cycle - 1))
        result_stamina = (wm.self().stamina()
                          - total_consume
                          + total_recover)

        if result_stamina < ServerParam.i().recover_dec_thr_value() + 205:
            return False

        return True

    def can_reach_after_dash(self,
                             n_turn: int,
                             n_dash: int,
                             ball_pos: Vector2D,
                             control_area: float,
                             save_recovery: bool,
                             dash_angle: AngleDeg,
                             back_dash: bool,
                             result_recovery,
                             self_cache: list):
        PLAYER_NOISE_RATE = 1 - ServerParam.i().player_rand() * 0.01
        MAX_POWER = ServerParam.i().max_dash_power()

        SP = ServerParam.i()
        wm = self._wm
        ptype = wm.self().player_type()

        my_inertia = wm.self().inertia_point(n_turn + n_dash)
        recover_dec_thr = SP.recover_dec_thr() * SP.stamina_max()

        dash_angle_minus = -dash_angle
        ball_rel = (ball_pos - wm.self().pos()).rotated_vector(dash_angle_minus)
        ball_noise = (wm.ball().pos().dist(ball_pos)
                      * SP.ball_rand()
                      * 0.5)
        noised_ball_x = ball_rel.x() + ball_noise

        # prepare loop variables
        # ORIGIN: first player pos.
        # X - axis: dash angle
        tmp_pos = ptype.inertia_travel(wm.self().vel(), n_turn)
        tmp_pos.rotate(dash_angle_minus)

        tmp_vel = wm.self().vel()
        tmp_vel *= ptype.player_decay() ** n_turn
        tmp_vel.rotate(dash_angle_minus)

        stamina_model = wm.self().stamina_model()
        stamina_model.simulate_waits(ptype, n_turn)

        prev_effort = stamina_model.effort()
        dash_power_abs = MAX_POWER
        # only consider about x of dash accel vector,
        # because current orientation is player's dash angle (included back dash case)
        # NOTE: dash_accel_x must be positive value.
        dash_accel_x = dash_power_abs * ptype.dash_rate(stamina_model.effort())

        can_over_speed_max = ptype.can_over_speed_max(dash_power_abs,
                                                      stamina_model.effort())
        first_dash_power = dash_power_abs * (-1 if back_dash else 1)
        for i in range(n_dash):
            # update dash power and accel
            available_power = (max(0, stamina_model.stamina() - recover_dec_thr)
                               if save_recovery
                               else stamina_model.stamina() + ptype.extra_stamina())
            if back_dash:
                available_power *= 0.5
            available_power = min_max(0, available_power, MAX_POWER)

            must_update_power = False
            if (available_power < dash_power_abs
                    or stamina_model.effort() < prev_effort
                    or (not can_over_speed_max
                        and dash_power_abs < available_power)):
                must_update_power = True

            if must_update_power:
                dash_power_abs = available_power
                dash_accel_x = dash_power_abs * ptype.dash_rate(stamina_model.effort())
                can_over_speed_max = ptype.can_over_speed_max(dash_power_abs,
                                                              stamina_model.effort())
                if i == 0:
                    first_dash_power = dash_power_abs * (-1 if back_dash else 1)

            # update vel
            tmp_vel.add_x(dash_accel_x)
            # power conservation, update accel magnitude and dashpower
            if can_over_speed_max and tmp_vel.r2() > ptype.player_speed_max2():
                tmp_vel.sub_x(dash_accel_x)
                max_dash_x = (ptype.player_speed_max2() - tmp_vel.y() ** 2) ** 0.5

                dash_accel_x = max_dash_x - tmp_vel.x()
                dash_power_abs = abs(dash_accel_x / ptype.dash_rate(stamina_model.effort()))
                tmp_vel.add_x(dash_accel_x)
                can_over_speed_max = ptype.can_over_speed_max(dash_power_abs,
                                                              stamina_model.effort())

            tmp_pos += tmp_vel
            tmp_vel *= ptype.player_decay()
            stamina_model.simulate_dash(ptype, dash_power_abs * (-1 if back_dash else 1))

            if tmp_pos.x() * PLAYER_NOISE_RATE + 0.1 > noised_ball_x:
                result_recovery = stamina_model.recovery()
                inertia_pos = ptype.inertia_point(tmp_pos, tmp_vel, n_dash - (i + 1))
                my_final_pos = wm.self().pos() + tmp_pos.rotate(dash_angle)
                if my_inertia.dist2(my_final_pos) > 0.01:
                    my_final_pos = Line2D(p1=my_inertia, p2=my_final_pos).projection(ball_pos)
                stamina_model.simulate_waits(ptype, n_dash - (i + 1))
                mode = (InterceptInfo.Mode.EXHAUST
                        if stamina_model.recovery() < wm.self().recovery()
                           and not stamina_model.capacity_is_empty()
                        else InterceptInfo.Mode.NORMAL)
                self_cache.append(InterceptInfo(mode,
                                                n_turn, n_dash,
                                                first_dash_power, 180.0 if back_dash else 0,
                                                my_final_pos,
                                                my_final_pos.dist(ball_pos),
                                                stamina_model.stamina()))
                return True, result_recovery

        player_travel = tmp_pos.r()
        player_noise = player_travel * SP.player_rand() * 0.5
        last_ball_dist = ball_rel.dist(tmp_pos)
        buf = 0.2

        buf += player_noise
        buf += ball_noise

        if last_ball_dist < max(control_area - 0.225, control_area - buf):
            my_final_pos = wm.self().pos() + tmp_pos.rotate(dash_angle)
            result_recovery = stamina_model.recovery()
            mode = (InterceptInfo.Mode.EXHAUST
                    if stamina_model.recovery() < wm.self().recovery()
                       and not stamina_model.capacity_is_empty()
                    else InterceptInfo.Mode.NORMAL)
            self_cache.append(InterceptInfo(mode,
                                            n_turn, n_dash,
                                            first_dash_power, 180.0 if back_dash else 0,
                                            my_final_pos, my_final_pos.dist(ball_pos),
                                            stamina_model.stamina()))
            return True, result_recovery
        return False, result_recovery

    def predict_final(self, max_cycle: int, self_cache: list):
        wm = self._wm
        me = wm.self()
        ptype = me.player_type()

        my_final_pos = me.inertia_point(100)
        ball_final_pos = wm.ball().inertia_point(100)
        goalie_mode = self.is_goalie_mode(ball_final_pos)
        control_area = ptype.catchable_area() - 0.15 if goalie_mode else ptype.kickable_area()
        dash_angle = me.body()
        n_turn, dash_angle, back_dash = self.predict_turn_cycle(100,
                                                                ball_final_pos,
                                                                control_area,
                                                                dash_angle)
        dash_dist = my_final_pos.dist(ball_final_pos)
        dash_dist -= control_area
        n_dash = ptype.cycles_to_reach_distance(dash_dist)

        if max_cycle > n_turn + n_dash:
            n_dash = max_cycle - n_turn

        stamina_model = me.stamina_model()
        stamina_model.simulate_waits(ptype, n_turn)
        stamina_model.simulate_dashes(ptype, n_dash, ServerParam.i().max_dash_power())
        self_cache.append(InterceptInfo(InterceptInfo.Mode.NORMAL,
                                        n_turn, n_dash,
                                        ServerParam.i().max_dash_power(), 0,
                                        ball_final_pos,
                                        0,
                                        stamina_model.stamina()))
