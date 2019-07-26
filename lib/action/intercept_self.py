from lib.action.intercept_info import InterceptInfo
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.vector_2d import Vector2D
from lib.player.object_player import PlayerObject
from lib.player.stamina_model import StaminaModel
from lib.player.world_model import WorldModel
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam


class SelfIntercept:
    def __init__(self, wm, ball_cache):
        self._wm: WorldModel = wm
        self._ball_cache = ball_cache

    def predict(self, max_cycle, self_cache):
        if len(self._ball_cache) < 2:
            dlog.add_text(Level.INTERCEPT, "no ball position cache :(")
            return

        save_recovery: bool = self._wm.self().stamina_model().capacity() != 0

        self.predict_one_step(self_cache)
        self.predict_short_step(max_cycle, save_recovery, self_cache)
        self.predict_long_step(max_cycle, save_recovery, self_cache)

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
        # TODO last kicker side for world
        return wm.self().goalie() and \
               wm.last_kicker_side() != wm.our_side() and \
               ball_next.x() < ServerParam.i().our_penalty_area_line_x() and \
               ball_next.absY() < ServerParam.i().penalty_area_half_width()

    def predict_one_dash(self, self_cache):
        pass

    def predict_short_step(self, max_cycle, save_recovery, self_cache):
        pass

    def predict_long_step(self, max_cycle, save_recovery, self_cache):
        pass
