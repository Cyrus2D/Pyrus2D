from lib.rcsc.server_param import ServerParam as SP
import pyrusgeom.soccer_math as smath

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel


def get_normal_dash_power(wm: 'WorldModel', s_recover_mode: bool):
    if wm.self().stamina_model().capacity_is_empty():
        return min(SP.i().max_dash_power(), wm.self().stamina() + wm.self().player_type().extra_stamina())

    self_min = wm.intercept_table().self_reach_cycle()
    mate_min = wm.intercept_table().teammate_reach_cycle()
    opp_min = wm.intercept_table().opponent_reach_cycle()
    ball_min_reach_cycle = min(self_min, mate_min, opp_min)

    if wm.self().stamina_model().capacity_is_empty():
        s_recover_mode = False
    elif wm.self().stamina() < SP.i().stamina_max() * 0.5:
        s_recover_mode = True
    elif wm.self().stamina() > SP.i().stamina_max() * 0.7:
        s_recover_mode = False

    dash_power = SP.i().max_dash_power()
    my_inc = wm.self().player_type().stamina_inc_max() * wm.self().recovery()

    # TODO wm.ourDefenseLineX() > wm.self().pos().x
    # TODO wm.ball().pos().x() < wm.ourDefenseLineX() + 20.0
    if wm.self().unum() <= 5 and wm.ball().inertia_point(ball_min_reach_cycle).x() < -20.0:
        dash_power = SP.i().max_dash_power()
    elif s_recover_mode:
        dash_power = my_inc - 25.0
        if dash_power < 0.0:
            dash_power = 0.0
    elif wm.exist_kickable_teammates() and wm.ball().dist_from_self() < 20.0:
        dash_power = min(my_inc * 1.1, SP.i().max_dash_power())
    elif wm.self().pos().x() > wm.offside_line_x():
        dash_power = SP.i().max_dash_power()
    elif wm.ball().pos().x() > 25.0 and wm.ball().pos().x() > wm.self().pos().x() + 10.0 and self_min < opp_min - 6 and mate_min < opp_min - 6:
        dash_power = smath.bound(SP.i().max_dash_power() * 0.1, my_inc * 0.5, SP.i().max_dash_power())
    else:
        dash_power = min(my_inc * 1.7, SP.i().max_dash_power())
    return dash_power, s_recover_mode
