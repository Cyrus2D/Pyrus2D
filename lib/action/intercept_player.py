from math import floor

from lib.math.soccer_math import bound
from lib.math.vector_2d import Vector2D
from lib.player.object_player import PlayerObject
from lib.player.templates import WorldModel
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam


class PlayerIntercept:
    def __init__(self, wm: WorldModel, ball_cache):
        self._wm = wm
        self._ball_cache = ball_cache

    def predict(self,
                player: PlayerObject,
                player_type: PlayerType,
                max_cycle: int):
        wm = self._wm
        penalty_x_abs = ServerParam.i().pitch_half_length() - ServerParam.i().penalty_area_length()
        penalty_y_abs = ServerParam.i().penalty_area_half_width()

        pos_count = min(player.seen_pos_count(), player.pos_count())
        player_pos = (player.seen_pos()
                      if player.seen_pos_count() <= player.pos_count()
                      else player.pos())
        min_cycle = 0
        ball_to_player = player_pos - wm.ball().pos()
        ball_to_player.rotate(-wm.ball().vel().th())
        min_cycle = int(floor(ball_to_player.absY()
                              / player_type.real_speed_max()))

        if player.is_tackling():
            min_cycle += max(0,
                             ServerParam.i().tackle_cycles() - player.tackle_count() - 2)

        min_cycle = max(0,
                        min_cycle - min(player.seen_pos_count(),
                                        player.pos_count()))
        if min_cycle > max_cycle:
            return self.predict_final(player, player_type)

        MAX_LOOP = min(max_cycle,
                       len(self._ball_cache))
        for cycle in range(min_cycle, MAX_LOOP):
            ball_pos: Vector2D = self._ball_cache[cycle]
            control_area = (player_type.catchable_area()
                            if (player.goalie()
                                and ball_pos.absX() > penalty_x_abs
                                and ball_pos.absY() < penalty_y_abs)
                            else player_type.kickable_area())

            if (control_area + player_type.real_speed_max() * (cycle + pos_count) + 0.5
                    < player_pos.dist(ball_pos)):
                # never reach
                continue
            if self.can_reach_after_turn_dash(cycle,
                                              player,
                                              player_type,
                                              control_area,
                                              ball_pos):
                return cycle

        return self.predict_final(player, player_type)

    def predict_final(self, player: PlayerObject, player_type: PlayerType):
        wm = self._wm
        penalty_x_abs = ServerParam.i().pitch_half_length() - ServerParam.i().penalty_area_length()
        penalty_y_abs = ServerParam.i().penalty_area_half_width()

        pos_count = min(player.seen_pos_count(), player.pos_count())
        ppos = (player.seen_pos()
                if player.seen_pos_count() <= player.pos_count()
                else player.pos())
        pvel = (player.seen_vel
                if player.seen_vel_count <= player.vel_count()
                else player.vel())

        ball_pos = self._ball_cache[-1]
        ball_step = len(self._ball_cache)

        control_area = (player_type.catchable_area()
                        if (player.goalie()
                            and ball_pos.absX() > penalty_x_abs
                            and ball_pos.absY() < penalty_y_abs)
                        else player_type.kickable_area())

        n_turn = self.predict_turn_cycle(100,
                                         player,
                                         player_type,
                                         control_area,
                                         ball_pos)

        inertia_pos = player_type.inertia_point(ppos, pvel, 100)
        dash_dist = inertia_pos.dist(ball_pos)
        dash_dist -= control_area

        if player.side() != wm.our_side():
            dash_dist -= player.dist_from_self * 0.03

        if dash_dist < 0:
            return ball_step

        n_dash = player_type.cycles_to_reach_distance(dash_dist)

        if player.side() != wm.our_side():
            n_dash -= bound(0, pos_count - n_turn, 10)
        else:
            n_dash -= bound(0, pos_count - n_turn, 1)

        n_dash = max(1, n_dash)

        return max(ball_step, n_turn + n_dash)

