from lib.debug.color import Color
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.vector_2d import Vector2D
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam


class InterceptInfo:
    def __init__(self):
        pass


class InterceptTable:
    def __init__(self):
        self._last_update_time: GameTime = GameTime(-10, -100)
        self._ball_cache = []
        self._max_cycle: int = 30

    def update(self, wm):
        # if self._last_update_time == wm.time():
        #     dlog.add_text(Level.INTERCEPT, "intercept updated befor :| it called agein")
        #
        self._last_update_time = wm.time()
        self.clear()

        if wm.time().cycle() < 1:  # TODO check game mode here
            return

        if not wm.self().pos().is_valid() or not wm.ball().pos().is_valid():
            dlog.add_text(Level.INTERCEPT, "self pos or ball pos is not valid")
            return

        self.create_ball_cache(wm)

    def clear(self):
        self._ball_cache = []

    def create_ball_cache(self, wm):
        SP = ServerParam.i()
        pitch_max_x = SP.pitch_half_length() + 5
        pitch_max_y = SP.pitch_half_width() + 5
        ball_decay = SP.ball_decay()

        ball_pos: Vector2D = wm.ball().pos()
        ball_vel: Vector2D = wm.ball().vel()

        self._ball_cache.append(ball_pos)

        for cycle in range(1, self._max_cycle + 1):
            # dlog.add_point(Level.INTERCEPT, pos=ball_pos, color=Color(string='blue'))
            dlog.add_circle(Level.INTERCEPT, r=0.1, center=ball_pos, fill=True, color=Color(string="blue"))
            dlog.add_text(Level.INTERCEPT, f"ballpos: {ball_pos}")
            ball_pos += ball_vel
            ball_vel *= ball_decay
            self._ball_cache.append(ball_pos)

            if cycle >= 5 and ball_vel.r() < 0.01 ** 2:
                # ball stopped
                break

            if ball_pos.absX() > pitch_max_x or ball_pos.absY() > pitch_max_y:
                # out of pitch
                break

        # TODO if len == 1 push ball pos again :| why??
