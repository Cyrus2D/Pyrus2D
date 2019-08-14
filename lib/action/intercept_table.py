from lib.action.intercept_info import InterceptInfo
from lib.action.intercept_player import PlayerIntercept
from lib.action.intercept_self import SelfIntercept
from lib.debug.color import Color
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.vector_2d import Vector2D
from lib.player.object_player import PlayerObject
from lib.player.templates import WorldModel
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType


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

    def self_reach_cycle(self):
        return self._self_reach_cycle

    def self_exhaust_reach_cycle(self):
        return self._self_exhaust_reach_cycle

    def teammate_reach_cycle(self):
        return self._teammate_reach_cycle

    def second_teammate_reach_cycle(self):
        return self._second_teammate_reach_cycle

    def goalie_reach_cycle(self):
        return self._goalie_reach_cycle

    def opponent_reach_cycle(self):
        return self._opponent_reach_cycle

    def second_opponent_reach_cycle(self):
        return self._second_opponent_reach_cycle

    def update(self, wm: WorldModel):
        # if self._last_update_time == wm.time(): # TODO uncomment it
        #     dlog.add_text(Level.INTERCEPT, "intercept updated befor :| it called agein")

        self._last_update_time = wm.time()
        self.clear()

        if wm.game_mode().type() == GameModeType.TimeOver or \
                wm.game_mode().type() == GameModeType.BeforeKickOff:
            return

        if not wm.self().pos().is_valid() or not wm.ball().pos().is_valid():
            dlog.add_text(Level.INTERCEPT, "self pos or ball pos is not valid")
            return

        self.create_ball_cache(wm)
        self.predict_self(wm)
        self.predict_opponent(wm)
        self.predict_teammate(wm)

        if self._fastest_teammate is not None:
            dlog.add_text(Level.INTERCEPT,
                          f"Intercept Teammate, fastest reach step={self._teammate_reach_cycle}"
                          f"teammate {self._fastest_teammate.unum()} {self._fastest_teammate.pos()}")
        if self._second_teammate is not None:
            dlog.add_text(Level.INTERCEPT,
                          f"Intercept Teammate2nd, fastest reach step={self._second_teammate_reach_cycle}"
                          f"teammate {self._second_teammate.unum()} {self._second_teammate.pos()}")
        if self._fastest_opponent is not None:
            dlog.add_text(Level.INTERCEPT,
                          f"Intercept Opponent, fastest reach step={self._opponent_reach_cycle}"
                          f"teammate {self._fastest_opponent.unum()} {self._fastest_opponent.pos()}")
        if self._second_opponent is not None:
            dlog.add_text(Level.INTERCEPT,
                          f"Intercept Opponent2nd, fastest reach step={self._second_opponent_reach_cycle}"
                          f"teammate {self._second_opponent.unum()} {self._second_opponent.pos()}")

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

        if wm.self().is_kickable():
            return

        for cycle in range(1, self._max_cycle + 1):
            ball_pos += ball_vel
            ball_vel *= ball_decay
            self._ball_cache.append(ball_pos.copy())

            if cycle >= 5 and ball_vel.r2() < 0.01 ** 2:
                # ball stopped
                break

            if ball_pos.absX() > pitch_max_x or ball_pos.absY() > pitch_max_y:
                # out of pitch
                break

        if len(self._ball_cache) == 1:
            self._ball_cache.append(ball_pos.copy())

        for b in self._ball_cache:
            dlog.add_circle(Level.INTERCEPT, r=0.1, center=b, fill=True, color=Color(string="blue"))

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

    def predict_opponent(self, wm: WorldModel):
        opponents = wm.opponents_from_ball()

        if wm.exist_kickable_opponents():
            dlog.add_text(Level.INTERCEPT,
                          "Intercept Opponent. exits kickable opponent")
            self._opponent_reach_cycle = 0
            for o in opponents:
                if o.is_ghost() or o.pos_count() > wm.ball().pos_count() + 1:
                    continue
                self._fastest_opponent = o
                dlog.add_text(Level.INTERCEPT,
                              f"fastest opp {self._fastest_opponent}")
                break
            return

        min_cycle = 1000
        second_min_cycle = 1000

        predictor = PlayerIntercept(wm, self._ball_cache)
        for it in opponents:
            if it.pos_count() >= 15:
                continue

            player_type = it.player_type()
            if player_type is None:
                dlog.add_text(Level.INTERCEPT,
                              f"intercept opponents faild to get player{it.unum()} type")
                continue
            cycle = predictor.predict(it, player_type,
                                      second_min_cycle)
            dlog.add_text(Level.INTERCEPT,
                          f"opp{it.unum()} {it.pos()} "
                          f"type={player_type.id()} cycle={cycle}")

            if cycle < second_min_cycle:
                second_min_cycle = cycle
                self._second_opponent = it

                if second_min_cycle < min_cycle:
                    # swap :)
                    min_cycle, second_min_cycle = second_min_cycle, min_cycle
                    self._fastest_opponent, self._second_opponent = self._second_opponent, self._fastest_opponent

        if self._second_opponent is not None and second_min_cycle < 1000:
            self._second_opponent_reach_cycle = second_min_cycle

        if self._fastest_opponent is not None and min_cycle < 1000:
            self._opponent_reach_cycle = min_cycle

    def predict_teammate(self, wm: WorldModel):
        teammates = wm.teammates_from_ball()

        if wm.exist_kickable_teammates():
            dlog.add_text(Level.INTERCEPT,
                          "Intercept Teammates. exits kickable teammate")
            self._teammate_reach_cycle = 0
            for t in teammates:
                if t.is_ghost() or t.pos_count() > wm.ball().pos_count() + 1:
                    continue
                self._fastest_teammate = t
                dlog.add_text(Level.INTERCEPT,
                              f"fastest tm {self._fastest_teammate}")
                break
            return

        min_cycle = 1000
        second_min_cycle = 1000

        predictor = PlayerIntercept(wm, self._ball_cache)
        for it in teammates:
            if it.pos_count() >= 10:
                continue

            player_type = it.player_type()
            if player_type is None:
                dlog.add_text(Level.INTERCEPT,
                              f"intercept teammate faild to get player{it.unum()} type")
                continue

            cycle = predictor.predict(it, player_type,
                                      second_min_cycle)
            dlog.add_text(Level.INTERCEPT,
                          f"tm{it.unum()} {it.pos()} "
                          f"type={player_type.id()} cycle={cycle}")

            if it.goalie():
                self._goalie_reach_cycle = cycle
            elif cycle < second_min_cycle:
                second_min_cycle = cycle
                self._second_teammate = it

                if second_min_cycle < min_cycle:
                    # swap :)
                    min_cycle, second_min_cycle = second_min_cycle, min_cycle
                    self._fastest_teammate, self._second_teammate = self._second_teammate, self._fastest_teammate

        if self._second_teammate is not None and second_min_cycle < 1000:
            self._second_teammate_reach_cycle = second_min_cycle

        if self._fastest_teammate is not None and min_cycle < 1000:
            self._teammate_reach_cycle = min_cycle

    def self_cache(self):
        return self._self_cache
