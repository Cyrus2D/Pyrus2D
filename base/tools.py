from lib.math.geom_2d import *
from lib.rcsc.server_param import ServerParam
from lib.rcsc.player_type import PlayerType
from lib.player.templates import *
from lib.rcsc.game_mode import GameModeType
from lib.action.kick_table import calc_max_velocity


class Tools:
    @staticmethod
    def predict_player_turn_cycle(ptype: PlayerType, player_body: AngleDeg, player_speed, target_dist,
                                  target_angle: AngleDeg, dist_thr, use_back_dash):
        sp = ServerParam.i()
        n_turn = 0
        angle_diff = (target_angle - player_body).abs()

        if use_back_dash and target_dist < 5.0 and angle_diff > 90.0 and sp.min_dash_power() < -sp.max_dash_power() + 1.0:
            angle_diff = abs( angle_diff - 180.0 )

        turn_margin = 180.0
        if dist_thr < target_dist:
            turn_margin = max( 15.0, AngleDeg.asin_deg( dist_thr / target_dist ) )

        speed = float(player_speed)
        while angle_diff > turn_margin:
            angle_diff -= ptype.effective_turn( sp.max_moment(), speed )
            speed *= ptype.player_decay()
            n_turn += 1

        return n_turn

    @staticmethod
    def predict_kick_count(wm: WorldModel, kicker, first_ball_speed, ball_move_angle: AngleDeg):
        if wm.game_mode().type() != GameModeType.PlayOn and not wm.game_mode().is_penalty_kick_mode():
            return 1

        if kicker == wm.self().unum() and wm.self().is_kickable():
            max_vel = calc_max_velocity(ball_move_angle, wm.self().kick_rate(), wm.ball().vel())
            if max_vel.r2() >= pow( first_ball_speed, 2):
                return 1
        if first_ball_speed > 2.5:
            return 3
        elif first_ball_speed > 1.5:
            return 2
        return 1

    @staticmethod
    def estimate_min_reach_cycle(player_pos: Vector2D, player_speed_max, target_first_point: Vector2D, target_move_angle: AngleDeg):
        target_to_player: Vector2D = (player_pos - target_first_point).rotated_vector(-target_move_angle)
        if target_to_player.x() < -1.0:
            return -1
        else:
            return max( 1, int(target_to_player.absY() / player_speed_max))

    @staticmethod
    def get_nearest_teammate_unum(wm: WorldModel, position: Vector2D, unums=[x for x in range(1, 12)]):
        unum = 0
        min_dist2 = 1000
        for i in unums:
            d2 = wm.our_player(i).pos().dist2( position )
            if d2 < min_dist2:
                min_dist2 = d2
                unum = i

        return unum
