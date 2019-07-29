from math import ceil

from lib.action.intercept_info import InterceptInfo
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.angle_deg import AngleDeg
from lib.math.segment_2d import Segment2D
from lib.math.soccer_math import bound, frange
from lib.math.vector_2d import Vector2D
from lib.player.object_ball import BallObject
from lib.player.object_player import PlayerObject
from lib.player.stamina_model import StaminaModel
from lib.player.templates import WorldModel
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam


class SelfIntercept:
    def __init__(self, wm, ball_cache):
        self._wm: WorldModel = wm
        self._ball_cache = ball_cache
        self._max_short_step = 5

    def predict(self, max_cycle, self_cache: list):
        if len(self._ball_cache) < 2:
            dlog.add_text(Level.INTERCEPT, "no ball position cache :(")
            return

        save_recovery: bool = self._wm.self().stamina_model().capacity() != 0

        self.predict_one_step(self_cache)
        self.predict_short_step(max_cycle, save_recovery, self_cache)
        self.predict_long_step(max_cycle, save_recovery, self_cache)

        self_cache.sort()  # TODO check this
        dlog.add_text(Level.INTERCEPT, "self pred all sorted intercept")
        for ii in self_cache:
            dlog.add_text(Level.INTERCEPT, f"{ii}")

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
        SP = ServerParam.i()
        wm: WorldModel = self._wm
        me: PlayerObject = wm.self()

        my_next: Vector2D = me.pos() + me.vel()
        ball_next: Vector2D = wm.ball().pos() + wm.ball().vel()
        goalie_mode: bool = self.is_goalie_mode(ball_next)
        control_area: float = me.player_type().catchable_area() if \
            goalie_mode else \
            me.player_type().kickable_area()
        next_ball_rel: Vector2D = (ball_next - my_next).rotated_vector(-me.body())  # WHAT THE FUUCKKKK
        ball_noise: float = wm.ball().vel().r() * SP.ball_rand()
        next_ball_dist: float = next_ball_rel.r()

        # out of control area
        if next_ball_dist > control_area - 0.15 - ball_noise:
            dlog.add_text(Level.INTERCEPT, "self pred no dash out of control area")
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
            dlog.add_text(Level.INTERCEPT, "self pred no dash goalie mode success")
            return True

        # check kick effectiveness
        ptype: PlayerType = me.player_type()
        if next_ball_dist > ptype.player_size() + SP.ball_size():
            kick_rate: float = ptype.kick_rate(next_ball_dist,
                                               next_ball_rel.th().degree())
            next_ball_vel: Vector2D = wm.ball().vel() * SP.ball_decay()
            if SP.max_power() * kick_rate <= next_ball_vel.r() * SP.ball_decay() * 1.1:
                dlog.add_text(Level.INTERCEPT, "self pred no dash kickable, but maybe not control")
                return False

        # at least, player can stop the ball
        stamina_model = me.stamina_model()
        self_cache.append(InterceptInfo(InterceptInfo.Mode.NORMAL,
                                        1, 0,  # 1 turn
                                        0, 0,
                                        my_next,
                                        next_ball_dist,
                                        stamina_model.stamina()))
        dlog.add_text(Level.INTERCEPT, "self pred no dash success")
        return True

    def is_goalie_mode(self, ball_next) -> bool:
        wm = self._wm
        return wm.self().goalie() and \
               wm.last_kicker_side() != wm.our_side() and \
               ball_next.x() < ServerParam.i().our_penalty_area_line_x() and \
               ball_next.absY() < ServerParam.i().penalty_area_half_width()

    def predict_one_dash(self, self_cache):
        tmp_cache = []

        SP = ServerParam.i()
        wm: WorldModel = self._wm
        ball: BallObject = wm.ball()
        me: PlayerObject = wm.self()
        ptype: PlayerType = me.player_type()

        ball_next: Vector2D = ball.pos() + ball.vel()
        goalie_mode: bool = self.is_goalie_mode(ball_next)
        control_area: float = ptype.catchable_area() if \
            goalie_mode else \
            ptype.kickable_area()
        dash_angle_step: float = max(5, SP.dash_angle_step())
        min_dash_angle = SP.min_dash_angle() if -180 < SP.max_dash_angle() < 180 else \
            dash_angle_step * int(-180 / dash_angle_step)
        max_dash_angle = SP.max_dash_angle() + dash_angle_step * 0.5 if \
            -180 < SP.max_dash_angle() < 180 else \
            dash_angle_step * int(180 / dash_angle_step) - 1
        dlog.add_text(Level.INTERCEPT, f"self pred on dash min_angle={min_dash_angle}, max_angle={max_dash_angle}")

        for dirr in frange(min_dash_angle, max_dash_angle, dash_angle_step):
            dash_angle: AngleDeg = me.body() + SP.discretize_dash_angle(SP.normalize_dash_angle(dirr))
            dash_rate: float = me.dash_rate() * SP.dash_dir_rate(dirr)
            dlog.add_text(Level.INTERCEPT, f"self pred one dash dir={dirr}, angle={dash_angle}, dash_rate={dash_rate}")

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
                dlog.add_text(Level.INTERCEPT, "Register 1 dash intercept(1)")
                tmp_cache.append(info)
                continue

            # check max_power_dash
            if abs(forward_dash_power - SP.max_dash_power()) < 1 and \
                    abs(back_dash_power - SP.min_dash_power()) < 1:
                continue

            max_forward_accel = Vector2D.polar2vector(SP.max_dash_power() * dash_rate,
                                                      dash_angle)
            max_back_accel = Vector2D.polar2vector(SP.min_dash_power() * dash_rate,
                                                   dash_angle)
            ptype.normalize_accel(me.vel(), max_forward_accel)
            ptype.normalize_accel(me.vel(), max_back_accel)

            if self.predict_one_dash_adjust(dash_angle,
                                            max_forward_accel,
                                            max_back_accel,
                                            control_area,
                                            info):
                dlog.add_text(Level.INTERCEPT, "Register 1 dash intercept(2)")
                tmp_cache.append(info)
                continue

        if len(tmp_cache) == 0:
            return
        safety_ball_dist = max(control_area - 0.2 - ball.vel().r() * SP.ball_rand(),
                               ptype.player_size() + SP.ball_size() + ptype.kickable_margin() * 0.4)
        best: InterceptInfo = tmp_cache[0]
        for it in tmp_cache:
            if best.ball_dist() < safety_ball_dist and \
                    it.ball_dist() < safety_ball_dist:
                if best.stamina() < it.stamina():
                    best = it
            elif best.ball_dist() > it.ball_dist() or \
                    (abs(best.ball_dist() - it.ball_dist()) < 0.001 and
                     best.stamina() < it.stamina()):
                best = it
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
        dlog.add_text(Level.INTERCEPT,
                      f"self pred one dash adjust dir={dash_dir}, ball_rel={ball_rel}")
        dlog.add_text(Level.INTERCEPT,
                      f"_____ max_forward_accel={max_forward_accel} rel={forward_accel_rel}")
        dlog.add_text(Level.INTERCEPT,
                      f"_____ max_back_accel={max_back_accel} rel={back_accel_rel}")

        if ball_rel.absY() > control_buf or \
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
            dlog.add_text(Level.INTERCEPT,
                          f"self pred one dash adjust (1). dash_power={dash_power}")

        # big x difference x (>0)
        if dash_power < -999 and \
                forward_accel_rel.x() < ball_rel.x:
            enable_ball_dist = ball_rel.dist(forward_accel_rel)
            if enable_ball_dist < control_buf:
                dash_power = forward_accel_rel.x() / dash_rate
                dlog.add_text(Level.INTERCEPT,
                              f"self pred one dash adjust (2). not best." +
                              f"next_ball_dist={enable_ball_dist}, dash_power={dash_power}")

        # big x difference (<0)
        if dash_power < -999 and \
                ball_rel.x() < back_accel_rel.x():
            enable_ball_dist = ball_rel.dist(ball_rel)
            if enable_ball_dist < control_buf:
                dash_power = back_accel_rel.x() / dash_rate
                dlog.add_text(Level.INTERCEPT,
                              f"self pred one dash adjust (3). not best." +
                              f"next_ball_dist={enable_ball_dist}, dash_power={dash_power}")

        # check if adjustable
        if dash_power < -999 and \
                back_accel_rel.x() < ball_rel.x() < forward_accel_rel.x():
            dash_power = ball_rel.x() / dash_rate
            dlog.add_text(Level.INTERCEPT,
                          f"self pred one dash adjust (4). not best." +
                          f"just adjust X. dash_power={dash_power}")

        # register
        if dash_power < -999:
            dlog.add_text(Level.INTERCEPT, "self pred one dash adjust XXX FAILED")
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
        dlog.add_text(Level.INTERCEPT,
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
        best_ctrl_dist_forward = ptype.player_size() + ptype.kickable_margin() / 2 + ServerParam.i().ball_size()
        best_ctrl_dist_backward = ptype.player_size() + 0.3 * ptype.kickable_margin() + ServerParam.i().ball_size()

        # y diff is longer than best dist.
        # just put the ball on player's side
        if next_ball_rel.absY() > best_ctrl_dist_forward:
            return next_ball_rel.x() / dash_rate

        forward_trap_accel_x = next_ball_rel.x() - (best_ctrl_dist_forward ** 2 - next_ball_rel.y() ** 2) ** 0.5
        backward_trap_accel_x = next_ball_rel.x() + (best_ctrl_dist_backward ** 2 - next_ball_rel.y() ** 2) ** 0.5

        best_accel_x = 10000
        min_power = 10000

        x_step = (backward_trap_accel_x - forward_trap_accel_x) / 5
        for accel_x in frange(forward_trap_accel_x, backward_trap_accel_x, x_step):
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

        ball_to_self = (me.pos() - ball.pos()).rotated_vector(ball.vel().th())
        min_cycle = int(ceil(ball_to_self.absY() - ptype.kickable_area()) / ptype.real_speed_max())

        if min_cycle >= max_loop:
            return
        if min_cycle < 2:
            min_cycle = 2

        # ball_pos = ball.inertia

    def predict_long_step(self, max_cycle, save_recovery, self_cache):
        pass
