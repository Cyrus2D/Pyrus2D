import math
from lib.math.geom import *

def kick_rate(dist, dir_diff, kprate, bsize, psize, kmargin):
    return kprate * (1.0 - 0.25 * math.fabs(dir_diff) / 180.0 - 0.25 * (dist - bsize - psize) / kmargin)


def dir_rate(dir, back_dash_rate, side_dash_rate):
    if math.fabs( dir ) > 90.0:
        return back_dash_rate - ( ( back_dash_rate - side_dash_rate ) * ( 1.0 - (math.fabs( dir ) - 90.0 ) / 90.0 ))
    return side_dash_rate + ( ( 1.0 - side_dash_rate ) * ( 1.0 - math.fabs( dir ) / 90.0 ) )


def effective_turn(turn_moment, speed, inertiamoment):
    return turn_moment / (1.0 + inertiamoment * speed)


def final_speed(dash_power, dprate, effort, decay):
    return ((math.fabs(dash_power) * dprate * effort) / (1.0 - decay))


def can_over_speed_max(dash_power, dprate, effort, decay, speed_max):
    return ( math.fabs( dash_power ) * dprate * effort > speed_max * ( 1.0 - decay ) )


def inertia_n_step_travel(initial_vel :Vector2D, n_step, decay):
    tmp = Vector2D(initial_vel.x, initial_vel.y)
    tmp *= (( 1.0 - math.pow( decay, n_step)) / (1.0 - decay))
    return tmp


def inertia_n_step_point(initial_pos: Vector2D, initial_vel: Vector2D, n_step, decay):
    tmp = Vector2D(initial_pos.x, initial_pos.y)
    tmp += inertia_n_step_travel( initial_vel, n_step, decay );
    return tmp


def inertia_n_step_distance(initial_speed, n_step, decay):
    if type(n_step) == int:
        return initial_speed * ( 1.0 - math.pow( decay, n_step ) ) / ( 1.0 - decay )
    else:
        return initial_speed * (1.0 - math.pow( decay, n_step) ) / (1.0 - decay)


def inertia_final_travel( initial_vel: Vector2D, decay):
    tmp = Vector2D(initial_vel.x, initial_vel.y)
    tmp /= (1.0 - decay)
    return tmp


def inertia_final_point(initial_pos: Vector2D, initial_vel: Vector2D, decay):
    tmp = Vector2D(initial_pos.x, initial_pos.y)
    tmp += inertia_final_travel(initial_vel, decay)
    return tmp


def inertia_final_distance(initial_speed, decay):
    return initial_speed / (1.0 - decay)

def rint(f):
    fi = int(f)
    fi_diff = math.fabs(fi - f)
    fi_left = fi - 1
    fi_left_diff = math.fabs(fi_left - f)
    fi_right = fi + 1
    fi_right_diff = math.fabs(fi_right - f)
    if fi_diff < fi_left_diff and fi_diff < fi_right_diff:
        return fi
    elif fi_left_diff < fi_right_diff:
        return fi_left
    else:
        return fi_right

