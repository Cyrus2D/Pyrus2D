from lib.action.intercept_info import InterceptInfo
from lib.action.intercept_self import SelfIntercept
from lib.debug.color import Color
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.vector_2d import Vector2D
from lib.player.object_player import PlayerObject
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam


class InterceptTable:
    def __init__(self):
        self._last_update_time: GameTime = GameTime(-10, -100)
        self._max_cycle: int = 30

        self._ball_cache = []
        self._self_cache = []

        self._self_reach_cycle = 1000
        self._self_exhaust_reach_cycle = 1000
        self._teammate_reach_cycle = 1000
        self._second_teammate_reach_cycle = 1000
        self._goalie_reach_cycle = 1000
        self._opponent_reach_cycle = 1000
        self._second_opponent_reach_cycle = 1000

        self._fastest_teammate: PlayerObject = None
        self._second_teammate: PlayerObject = None
        self._fastest_opponent: PlayerObject = None
        self._second_opponent: PlayerObject = None

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
        self.predict_self(wm)
        self.predict_opponent(wm)
        self.predict_teammate()

    def clear(self):
        self._ball_cache = []

        self._self_reach_cycle = 1000
        self._self_exhaust_reach_cycle = 1000
        self._teammate_reach_cycle = 1000
        self._second_teammate_reach_cycle = 1000
        self._goalie_reach_cycle = 1000
        self._opponent_reach_cycle = 1000
        self._second_opponent_reach_cycle = 1000

        self._fastest_teammate = None
        self._second_teammate = None
        self._fastest_opponent = None
        self._second_opponent = None

        self._self_cache = []

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
        if len(self._ball_cache) == 1:
            self._ball_cache.append(ball_pos)

    def predict_self(self, wm):
        if wm.self().is_kickable():
            dlog.add_text(Level.INTERCEPT, "Intercept predict self already kickable")
            return

        max_cycle = min(self._max_cycle, len(self._ball_cache))
        predictor = SelfIntercept(wm, self._ball_cache)
        predictor.predict(max_cycle, self._self_cache)

        if len(self._self_cache) == 0:
            dlog.add_text(Level.INTERCEPT,
                          "Intercept self, self cache is empty")
            return

        min_cycle = self._self_reach_cycle
        exhaust_min_cycle = self._self_exhaust_reach_cycle

        it: InterceptInfo = None
        for it in self._self_cache:
            if it.mode() == InterceptInfo.Mode.NORMAL:
                if it.reach_cycle() < min_cycle:
                    min_cycle = it.reach_cycle()
                    break
            elif it.mode() == InterceptInfo.Mode.EXHAUST:
                if it.reach_cycle() < exhaust_min_cycle:
                    exhaust_min_cycle = it.reach_cycle()
                    break

        dlog.add_text(Level.INTERCEPT,
                      f"Intercept self, solution size={len(self._self_cache)}")
        self._self_reach_cycle = min_cycle
        self._self_exhaust_reach_cycle = exhaust_min_cycle
