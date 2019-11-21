"""
  \ file soccer_math
  \ brief math utility depending on RCSSServer2D

"""
from lib.math.geom_2d import *

EPS = 1.0e-8

"""
  \ brief calculate kick rate
  \ param dist distance from player to ball
  \ param dir_diff angle difference from player's body to ball
  \ param kprate player's kick power rate parameter
  \ param bsize ball radius
  \ param psize player radius
  \ param kmargin player's kickable area margin
  \ return rate of the kick power effect

"""


def kick_rate(dist, dir_diff, kprate, bsize, psize, kmargin):
    return kprate * (1.0 - 0.25 * math.fabs(dir_diff) / 180.0 - 0.25 * (dist - bsize - psize) / kmargin)


"""
  \ brief calculate effective dash power rate according to the input dash direction
  \ param dir relative dash direction
  \ param back_dash_rate server parameter
  \ param side_dash_rate server parameter
  \ return effective dash power rate
 """


def dir_rate(dir_r, back_dash_rate, side_dash_rate):
    if math.fabs(dir_r) > 90.0:
        return back_dash_rate - ((back_dash_rate - side_dash_rate) * (1.0 - (math.fabs(dir_r) - 90.0) / 90.0))
    return side_dash_rate + ((1.0 - side_dash_rate) * (1.0 - math.fabs(dir_r) / 90.0))


"""
  \ brief calculate effective turn moment.
  it may be useful to redefine self algorithm in movement action module
  \ param turn_moment value used by turn command
  \ param speed player's current speed
  \ param inertiamoment player's inertia moment parameter
  \ return calculated actual turn angle
"""


def effective_turn(turn_moment, speed, inertiamoment):
    return turn_moment / (1.0 + inertiamoment * speed)


"""
  \ brief calculate converged max speed, using "dash_power"
  \ param dash_power value used by dash command
  \ param dprate player's dash power rate parameter
  \ param effort player's effort parameter
  \ param decay player's decay parameter
  \ return achieved final speed

  NOTE: returned value should be compared with player_speed_max parameter
"""


def final_speed(dash_power, dprate, effort, decay):
    return (math.fabs(dash_power) * dprate * effort) / (1.0 - decay)


"""
  \ brief check if player's potential max speed is over player_speed_max
  parameter.
  \ param dash_power value used by dash command
  \ param dprate player's dash power rate parameter
  \ param effort player's effort parameter
  \ param speed_max player's limited speed parameter
  \ param decay player's decay parameter
  \ return True, player can over player_speed_max
"""


def can_over_speed_max(dash_power, dprate, effort, decay, speed_max):
    return math.fabs(dash_power) * dprate * effort > speed_max * (1.0 - decay)


"""
  \ brief estimate future travel after n steps only by inertia.
  No additional acceleration.
  \ param initial_vel object's first velocity
  \ param n_step number of total steps
  \ param decay object's decay parameter
  \ return vector of total travel
"""


def inertia_n_step_travel(initial_vel, n_step, decay):
    tmp = Vector2D(initial_vel.x(), initial_vel.y())
    tmp *= ((1.0 - math.pow(decay, n_step)) / (1.0 - decay))
    return tmp


"""
  \ brief estimate future point after n steps only by inertia.
  No additional acceleration
  \ param initial_pos object's first position
  \ param initial_vel object's first velocity
  \ param n_step number of total steps
  \ param decay object's decay parameter
  \ return coordinate of the reached point
"""


def inertia_n_step_point(initial_pos: Vector2D, initial_vel: Vector2D, n_step, decay):
    tmp = Vector2D(initial_pos.x(), initial_pos.y())
    tmp += inertia_n_step_travel(initial_vel, n_step, decay)
    return tmp


"""
  \ brief estimate travel distance only by inertia.
  No additional acceleration
  \ param initial_speed object's first speed
  \ param n_step number of total steps
  \ param decay object's decay parameter
  \ return total travel distance
"""


def inertia_n_step_distance(initial_speed, n_step, decay):
    if type(n_step) == int:
        return initial_speed * (1.0 - math.pow(decay, n_step)) / (1.0 - decay)
    else:
        return initial_speed * (1.0 - math.pow(decay, n_step)) / (1.0 - decay)


"""
  \ brief calculate total travel only by inertia movement.
  \ param initial_vel object's first velocity
  \ param decay object's decay parameter
  \ return final travel vector
"""


def inertia_final_travel(initial_vel: Vector2D, decay):
    tmp = Vector2D(initial_vel.x(), initial_vel.y())
    tmp /= (1.0 - decay)
    return tmp


"""
  \ brief calculate final reach point only by inertia.
  \ param initial_pos object's first position
  \ param initial_vel object's first velocity
  \ param decay object's decay parameter
  \ return coordinate of the reached point
"""


def inertia_final_point(initial_pos: Vector2D, initial_vel: Vector2D, decay):
    tmp = Vector2D(initial_pos.x(), initial_pos.y())
    tmp += inertia_final_travel(initial_vel, decay)
    return tmp


"""
  \ brief calculate total travel distance only by inertia.
  \ param initial_speed object's first speed
  \ param decay object's decay parameter
  \ return distance value that the object reaches
"""


def inertia_final_distance(initial_speed, decay):
    return initial_speed / (1.0 - decay)


"""
    \ brief Rounds the floating-point argument f to an integer value (in floating-point format), using the current rounding mode. 
    \ param f floating point value
    \ return If no errors occur, the nearest integer value to f, according to the current rounding mode, is returned.a
"""


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


def calc_first_term_geom_series(sums, r, length):
    return sums * (1.0 - r) / (1.0 - math.pow(r, length))


def bound(a, b, c):
    return min(max(a, b), c)


def min_max(low, x, high):
    return min(max(low, x), high)


"""
     \ brief  Use float number in range() function
     \ param start the start number
     \ param stop the end number
     \ param step start += step until end
     \ return float number
"""


def frange(start, stop=None, step=None):
    # if stop and step argument is null set start=0.0 and step = 1.0
    if stop is None:
        stop = start + 0.0
        start = 0.0
    if step is None:
        step = 1.0
    while True:
        if step > 0 and start >= stop:
            break
        elif step < 0 and start <= stop:
            break
        yield start
        start = start + step


SERVER_EPS = 1.0e-10

# localization

"""
  \ brief quantize a floating point number
  \ param value value to be rounded
  \ param qstep round precision
  \ return rounded value

  same as define Quantize(v,q) ((rint((v)/(q)))*(q))
"""


def quantize(value,
             qstep):
    return rint(value / qstep) * qstep


"""
  \ brief calculate quantized distance value about dist quantization
  \ param unq_dist actual distance
  \ param qstep server parameter
  \ return quantized distance
"""


def quantize_dist(unq_dist,
                  qstep):
    return quantize(math.exp
                    (quantize(math.log
                              (unq_dist + SERVER_EPS), qstep)), 0.1)


"""
  \ brief calculate minimal value by inverse quantize function
  \ param dist quantized distance
  \ param qstep server parameter
  \ return minimal distance within un quantized distance range
"""


def unquantize_min(dist,
                   qstep):
    return (rint(dist / qstep) - 0.5) * qstep


"""
  \ brief calculate maximal value by inverse quantize function
  \ param dist quantized distance
  \ param qstep server parameter
  \ return maximal distance within un quantized distance range
"""


def unquantize_max(dist,
                   qstep):
    return (rint(dist / qstep) + 0.5) * qstep


"""add in servers"""
"""
  \ brief calculate wind effect
  \ param speed current object's speed
  \ param weight object's speed
  \ param wind_force server parameter
  \ param wind_dir server parameter
  \ param wind_weight server parameter
  \ param wind_rand server parameter
  \ param wind_error error value that is calculated by self method
  \ return wind effect acceleration
"""


def wind_effect(speed,
                weight,
                wind_force,
                wind_dir,
                wind_weight,
                wind_rand,
                wind_error: Vector2D):
    wind_vec = Vector2D()
    wind_vec.polar2vector(wind_force, wind_dir)

    if wind_error:
        wind_error.assign(speed * wind_vec.x * wind_rand
                          / (weight * wind_weight),
                          speed * wind_vec.y * wind_rand
                          / (weight * wind_weight))

    return Vector2D(speed * wind_vec.x / (weight * wind_weight),
                    speed * wind_vec.y / (weight * wind_weight))


"""-------------------------------------------------------------------"""
"""
  \ brief calculate min max error range by inverse quantize function
  \ param see_dist seen(quantized) distance
  \ param qstep server parameter
  \ return error value of inverse un quantized distance
"""


def unquantize_error(see_dist, qstep):
    min_dist = (math.exp(unquantize_min(math.log(unquantize_min(see_dist, 0.1)), qstep)) - SERVER_EPS)
    max_dist = (math.exp(unquantize_max(math.log(unquantize_max(see_dist, 0.1)), qstep)) - SERVER_EPS)
    return math.fabs(max_dist - min_dist)


"""------------------------------------------------------------------"""
"""
  \ brief caluculate the length of a geometric series
  \ param first_term value of the first term
  \ param r multiplication ratio
  \ param sum sum of a geometric series
  \ return a round number of the length of geometric series
"""


def calc_length_geom_series(first_term, sum, r):
    if first_term <= SERVER_EPS or sum < 0.0 or r <= SERVER_EPS:
        return -1.0
    if sum <= SERVER_EPS:
        return 0.0
    tmp = 1.0 + sum * (r - 1.0) / first_term
    if tmp <= SERVER_EPS:
        return -1.0
    return math.log( tmp ) / math.log( r )
