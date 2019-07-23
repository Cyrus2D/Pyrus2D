"""
  \ file soccer_math
  \ brief math utility depending on RCSSServer2D

"""

from lib.math.geom import *
import numpy as np

SERVER_EPS = 1.0e-10

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


def kick_rate(dist: float, dir_diff: float, kprate: float, bsize: float, psize: float, kmargin: float):
    return kprate * (1.0
                     - 0.25 * math.fabs(dir_diff) / 180.0
                     - 0.25 * (dist - bsize - psize) / kmargin)


# dash command related

"""
  \ brief calculate effective dash power rate according to the input dash direction
  \ param dir relative dash direction
  \ param back_dash_rate server parameter
  \ param side_dash_rate server parameter
  \ return effective dash power rate
 """


def dir_rate(dir_r, back_dash_rate, side_dash_rate):
    if math.fabs(dir_r) > 90.0:
        return back_dash_rate - (back_dash_rate - side_dash_rate) * (1.0 - (math.fabs(dir_r) - 90.0) / 90.0)
    else:
        return side_dash_rate + ((1.0 - side_dash_rate) * (1.0 - math.fabs(dir_r) / 90.0))


"""
  \ brief calculate effective turn moment.
  it may be useful to redefine self algorithm in movement action module
  \ param turn_moment value used by turn command
  \ param speed player's current speed
  \ param inertiamoment player's inertia moment parameter
  \ return calculated actual turn angle
"""


def effective_turn(turn_moment,
                   speed,
                   inertiamoment):
    return turn_moment / (1.0 + inertiamoment * speed)


# dash command related

"""
  \ brief calculate converged max speed, using "dash_power"
  \ param dash_power value used by dash command
  \ param dprate player's dash power rate parameter
  \ param effort player's effort parameter
  \ param decay player's decay parameter
  \ return achieved final speed

  NOTE: returned value should be compared with player_speed_max parameter
"""


def final_speed(dash_power: float,
                dprate: float,
                effort: float,
                decay: float):
    # if player continue to run using the same dash power
    # achieved speed at n step later is sum of infinite geometric series

    # not ! NOTE not !
    # You must compare self value to the PlayerType.playerSpeedMax()

    # return ( (dash_power * dprate * effort) # == accel
    #         * (1.0 / (1.0 - decay)) ); # == sum inf geom series
    return ((math.fabs(dash_power) * dprate * effort)  # == accel
            / (1.0 - decay))  # == sum inf geom series


"""-------------------------------------------------------------------"""
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


def can_over_speed_max(dash_power: float,
                       dprate: float,
                       effort: float,
                       decay: float,
                       speed_max: float):
    return (math.fabs(dash_power) * dprate * effort  # max accel
            > speed_max * (1.0 - decay))  # is over speed decay


# predictor method for inertia movement

"""-------------------------------------------------------------------"""
"""
  \ brief estimate future travel after n steps only by inertia.
  No additional acceleration.
  \ param initial_vel object's first velocity
  \ param n_step number of total steps
  \ param decay object's decay parameter
  \ return vector of total travel
"""


def inertia_n_step_travel(initial_vel: Vector2D, n_step, decay):
    tmp = initial_vel * ((1.0 - math.pow(decay, n_step)) / (1.0 - decay))
    return tmp


"""-------------------------------------------------------------------"""
"""
  \ brief estimate future point after n steps only by inertia.
  No additional acceleration
  \ param initial_pos object's first position
  \ param initial_vel object's first velocity
  \ param n_step number of total steps
  \ param decay object's decay parameter
  \ return coordinate of the reached point
"""


def inertia_n_step_point(initial_pos: Vector2D,
                         initial_vel: Vector2D, n_step, decay):
    tmp = initial_pos + inertia_n_step_travel(initial_vel, n_step, decay)
    return tmp


"""-------------------------------------------------------------------"""
"""
  \ brief estimate travel distance only by inertia.
  No additional acceleration
  \ param initial_speed object's first speed
  \ param n_step number of total steps
  \ param decay object's decay parameter
  \ return total travel distance
"""


def inertia_n_step_distance(initial_speed, n_step, decay):
    return initial_speed * (1.0 - math.pow(decay, n_step)) / (1.0 - decay)


"""-------------------------------------------------------------------"""
"""
  \ brief calculate total travel only by inertia movement.
  \ param initial_vel object's first velocity
  \ param decay object's decay parameter
  \ return final travel vector
"""


def inertia_final_travel(initial_vel: Vector2D,
                         decay):
    tmp = initial_vel / (1.0 - decay)
    return tmp


"""-------------------------------------------------------------------"""
"""
  \ brief calculate final reach point only by inertia.
  \ param initial_pos object's first position
  \ param initial_vel object's first velocity
  \ param decay object's decay parameter
  \ return coordinate of the reached point
"""


def inertia_final_point(initial_pos: Vector2D,
                        initial_vel: Vector2D,
                        decay):
    tmp = Vector2D(initial_pos) + inertia_final_travel(initial_vel, decay)
    return tmp


"""-------------------------------------------------------------------"""
"""
  \ brief calculate total travel distance only by inertia.
  \ param initial_speed object's first speed
  \ param decay object's decay parameter
  \ return distance value that the object reaches
"""


def inertia_final_distance(initial_speed,
                           decay):
    return initial_speed / (1.0 - decay)


# localization

"""-------------------------------------------------------------------"""
"""
  \ brief quantize a floating point number
  \ param value value to be rounded
  \ param qstep round precision
  \ return rounded value

  same as define Quantize(v,q) ((np.rint((v)/(q)))*(q))
"""


def quantize(value,
             qstep):
    return np.rint(value / qstep) * qstep


"""-------------------------------------------------------------------"""
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


"""-------------------------------------------------------------------"""
"""
  \ brief calculate minimal value by inverse quantize function
  \ param dist quantized distance
  \ param qstep server parameter
  \ return minimal distance within un quantized distance range
"""


def unquantize_min(dist,
                   qstep):
    return (np.rint(dist / qstep) - 0.5) * qstep


"""-------------------------------------------------------------------"""
"""
  \ brief calculate maximal value by inverse quantize function
  \ param dist quantized distance
  \ param qstep server parameter
  \ return maximal distance within un quantized distance range
"""


def unquantize_max(dist,
                   qstep):
    return (np.rint(dist / qstep) + 0.5) * qstep


"""-------------------------------------------------------------------"""
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
