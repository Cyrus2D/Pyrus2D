from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.vector_2d import Vector2D
from lib.player.world_model import WorldModel
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
        goalie_mode: bool = wm.self().goalie() and \
                            wm.last_kicker_side() != wm.our_side() and \
                            ball_next.x() < ServerParam.i().our_penalty_area_line_x() and \
                            ball_next.absY() < ServerParam.i().penalty_area_half_width()
        control_area: float = wm.self().player_type().catchable_area() if \
            goalie_mode else \
            wm.self().player_type().kickable_aria()

        # dist is to far never reach with one dash
        if wm.ball().dist_from_self() > \
                ServerParam.i().ball_speed_max() \
                + wm.self().player_type().real_speed_max() \
                + control_area:
            return
        if self.predict_no_dash(self_cache):
            return
        self.predict_one_dash(self_cache)

    def predict_short_step(self, max_cycle, save_recovery, self_cache):
        pass

    def predict_long_step(self, max_cycle, save_recovery, self_cache):
        pass
