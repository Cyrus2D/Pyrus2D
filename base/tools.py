from lib.math.geom_2d import *
from lib.rcsc.server_param import ServerParam
from lib.rcsc.player_type import PlayerType


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
