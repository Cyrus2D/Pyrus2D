from math import floor

from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.soccer_math import bound, inertia_n_step_point
from pyrusgeom.vector_2d import Vector2D
from lib.player.object_player import PlayerObject
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel


class PlayerIntercept:
    def __init__(self, wm: 'WorldModel', ball_cache):
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
        min_cycle = int(floor(ball_to_player.abs_y()
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
                                and ball_pos.abs_x() > penalty_x_abs
                                and ball_pos.abs_y() < penalty_y_abs)
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
        pvel = (player.seen_vel()
                if player.seen_vel_count() <= player.vel_count()
                else player.vel())

        ball_pos = self._ball_cache[-1]
        ball_step = len(self._ball_cache)

        control_area = (player_type.catchable_area()
                        if (player.goalie()
                            and ball_pos.abs_x() > penalty_x_abs
                            and ball_pos.abs_y() < penalty_y_abs)
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
            dash_dist -= player.dist_from_self() * 0.03

        if dash_dist < 0:
            return ball_step

        n_dash = player_type.cycles_to_reach_distance(dash_dist)

        if player.side() != wm.our_side():
            n_dash -= bound(0, pos_count - n_turn, 10)
        else:
            n_dash -= bound(0, pos_count - n_turn, 1)

        n_dash = max(1, n_dash)

        return max(ball_step, n_turn + n_dash)

    def predict_turn_cycle(self,
                           cycle: int,
                           player: PlayerObject,
                           player_type: PlayerType,
                           control_area: float,
                           ball_pos: Vector2D):
        ppos = (player.seen_pos()
                if player.seen_pos_count() <= player.pos_count()
                else player.pos())
        pvel = (player.seen_vel()
                if player.seen_vel_count() <= player.vel_count()
                else player.vel())

        inertia_pos = player_type.inertia_point(ppos, pvel, cycle)
        target_rel = ball_pos - inertia_pos
        target_dist = target_rel.r()
        turn_margin = 180
        if control_area < target_dist:
            turn_margin = AngleDeg.asin_deg(control_area / target_dist)
        turn_margin = max(turn_margin, 12)

        angle_diff = (target_rel.th() - player.body()).abs()

        if (target_dist < 5  # XXX MAGIC NUMBER XXX :|
                and angle_diff > 90):
            # assume back dash
            angle_diff = 180 - angle_diff

        n_turn = 0
        speed = player.vel().r()
        while angle_diff > turn_margin:
            max_turn = player_type.effective_turn(ServerParam.i().max_moment(),
                                                  speed)
            angle_diff -= max_turn
            speed *= player_type.player_decay()
            n_turn += 1

        return n_turn

    def can_reach_after_turn_dash(self,
                                  cycle: int,
                                  player: PlayerObject,
                                  player_type: PlayerType,
                                  control_area: float,
                                  ball_pos: Vector2D):
        n_turn = self.predict_turn_cycle(cycle,
                                         player,
                                         player_type,
                                         control_area,
                                         ball_pos)

        n_dash = cycle - n_turn
        if n_dash < 0:
            return False

        return self.can_reach_after_dash(n_turn,
                                         n_dash,
                                         player,
                                         player_type,
                                         control_area,
                                         ball_pos)

    def can_reach_after_dash(self,
                             n_turn: int,
                             max_dash: int,
                             player: PlayerObject,
                             player_type: PlayerType,
                             control_area: float,
                             ball_pos: Vector2D):
        wm = self._wm
        pos_count = min(player.seen_pos_count(), player.pos_count())
        ppos = (player.seen_pos()
                if player.seen_pos_count() <= player.pos_count()
                else player.pos())
        pvel = (player.seen_vel()
                if player.seen_vel_count() <= player.vel_count()
                else player.vel())

        player_pos = inertia_n_step_point(ppos, pvel,
                                          n_turn + max_dash,
                                          player_type.player_decay())

        player_to_ball = ball_pos - player_pos
        player_to_ball_dist = player_to_ball.r()
        player_to_ball_dist -= control_area

        if player_to_ball_dist < 0:
            return True

        estimate_dash = player_type.cycles_to_reach_distance(player_to_ball_dist)
        n_dash = estimate_dash
        if player.side != wm.our_side():
            n_dash -= bound(0,
                            pos_count - n_turn,
                            min(6, wm.ball().seen_pos_count() + 1))
        else:
            n_dash -= bound(0,
                            pos_count - n_turn,
                            min(1, wm.ball().seen_pos_count()))

        if player.is_tackling():
            n_dash += max(0, ServerParam.i().tackle_cycles() - player.tackle_count() - 2)

        if n_dash <= max_dash:
            return True
        return False
