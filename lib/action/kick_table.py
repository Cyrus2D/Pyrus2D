"""
  \ file kick_table.py
  \ brief kick table class File to generate smart kick.
"""

from lib.player.world_model import *
from lib.rcsc.game_time import *
from lib.rcsc.player_type import *
from lib.rcsc.server_param import *
from lib.math.soccer_math import *
from enum import Enum

"""
  \ enum Flag
  \ brief status bit flags
"""


class Flag(Enum):
    SAFETY = 0x0000
    NEXT_TACKLEABLE = 0x0001
    NEXT_KICKABLE = 0x0002
    TACKLEABLE = 0x0004
    KICKABLE = 0x0008
    SELF_COLLISION = 0x0010
    RELEASE_INTERFERE = 0x0020
    MAYBE_RELEASE_INTERFERE = 0x0040
    OUT_OF_PITCH = 0x0080
    KICK_MISS_POSSIBILITY = 0x0100


NEAR_SIDE_RATE = 0.3  # < kickable margin rate for the near side sub-target
MID_RATE = 0.5  # < kickable margin rate for the middle distance sub-target
FAR_SIDE_RATE = 0.7  # < kickable margin rate for the far side sub-target
MAX_DEPTH = 2
STATE_DIVS_NEAR = 8
STATE_DIVS_MID = 12
STATE_DIVS_FAR = 15
NUM_STATE = STATE_DIVS_NEAR + STATE_DIVS_MID + STATE_DIVS_FAR

DEST_DIR_DIVS = 72,  # step: 5 degree

MAX_TABLE_SIZE = 256,

"""
  \ class State
  \ brief class to represent a kick intermediate state
"""


class State:
    # < index of self point
    # < distance from self
    # < position relative to player's body
    # < kick rate
    # < status bit flag

    """
      \ brief construct an illegal state object
        OR
      \ brief construct a legal state object. flag is set to SAFETY.
      \ param index index number of self state
      \ param dist distance from self
      \ param pos global position
      \ param kick_rate kick rate at self state
     """

    def __init__(self, *args):
        if len(args) == 0:
            self.index_ = -1
            self.dist_ = 0.0
            self.kick_rate_ = 0.0
            self.flag_ = 0xFFFF
        else:
            self.index_ = args[0]
            self.dist_ = args[1]
            self.pos_ = args[2]
            self.kick_rate_ = args[3]
            self.flag_ = Flag.SAFETY


"""
  \ class Path
  \ brief used as a heuristic knowledge. path representation between two states
"""


class Path:
    # < index of origin state
    # < index of destination state
    # < reachable ball max speed
    # < kick power to generate max_speed_

    """
      \ brief construct a kick path object
      \ param origin index of origin state
      \ param destination index of destination state
     """

    def __init__(self, origin, destination):
        self.origin_ = origin
        self.dest_ = destination
        self.max_speed_ = 0.0
        self.power_ = 1000.0

    """
      \ class Sequence
      \ brief simulated kick sequence
     """

    class Sequence:
        # < safety level flags. usually the combination of State flags
        # not < ball positions
        # < released ball speed
        # < estimated last kick power
        # < evaluated score of self sequence

        """
          \ brief construct an illegal sequence object
            OR
          \ brief copy constructor
          \ param arg another instance
         """

        def __init__(self, *args):
            if len(args) == 0:
                self.flag_ = 0x0000
                self.pos_list_ = []
                self.speed_ = 0.0
                self.power_ = 10000.0
                self.score_ = 0.0
            if len(args) == 1:
                self.flag_ = args[0].flag_
                self.pos_list_ = args[0].pos_list_
                self.speed_ = args[0].speed_
                self.power_ = args[0].power_
                self.score_ = args[0].score_


"""
 \ brief calculate the distance of near side sub-target
 \ param player_type calculated PlayerType
 \ return distance from the center of the player
"""


def calc_near_dist(player_type: PlayerType):
    #       0.3 + 0.6*0.3 + 0.085 = 0.565
    # near: 0.3 + 0.7*0.3 + 0.085 = 0.595
    #       0.3 + 0.8*0.3 + 0.085 = 0.625
    return bound(player_type.player_size() + ServerParam.i().ball_size() + 0.1,
                 (player_type.player_size()
                  + (player_type.kickable_margin() * NEAR_SIDE_RATE)
                  + ServerParam.i().ball_size()),
                 player_type.kickable_area() - 0.2)


"""
  \ brief calculate the distance of middle distance sub-target
  \ param player_type calculated PlayerType
  \ return distance from the center of the player
"""


def calc_mid_dist(player_type: PlayerType):
    #      0.3 + 0.6*0.5 + 0.085 = 0.705
    # mid: 0.3 + 0.7*0.5 + 0.085 = 0.735
    #      0.3 + 0.8*0.5 + 0.085 = 0.765
    return bound(player_type.player_size() + ServerParam.i().ball_size() + 0.1,
                 (player_type.player_size()
                  + (player_type.kickable_margin() * MID_RATE)
                  + ServerParam.i().ball_size()),
                 player_type.kickable_area() - 0.2)


"""
  \ brief calculate the distance of far side sub-target
  \ param player_type calculated PlayerType
  \ return distance from the center of the player
"""


def calc_far_dist(player_type: PlayerType):
    #      0.3 + 0.6*0.7 + 0.085 = 0.865 (=0.985-0.12 . 0.785)
    # far: 0.3 + 0.7*0.7 + 0.085 = 0.875 (=1.085-0.21)
    #      0.3 + 0.8*0.7 + 0.085 = 0.945 (=1.185-0.24)

    #      0.3 + 0.6*0.68 + 0.085 = 0.793 (=0.985-0.192 . 0.760)
    # far: 0.3 + 0.7*0.68 + 0.085 = 0.861 (=1.085-0.224 . 0.860)
    #      0.3 + 0.8*0.68 + 0.085 = 0.929 (=1.185-0.256)

    #      0.3 + 0.6*0.675 + 0.085 = 0.79   (=0.985-0.195)
    # far: 0.3 + 0.7*0.675 + 0.085 = 0.8575 (=1.085-0.2275)
    #      0.3 + 0.8*0.675 + 0.085 = 0.925  (=1.185-0.26)

    return bound(player_type.player_size() + ServerParam.i().ball_size() + 0.1,
                 (player_type.player_size()
                  + (player_type.kickable_margin() * FAR_SIDE_RATE)
                  + ServerParam.i().ball_size()),
                 player_type.kickable_area() - 0.2)
    # player_type.kickable_area() - 0.22 )


"""
  \ brief calculate maximum velocity for the target angle by one step kick with krate and ball_vel
  \ param target_angle target angle of the next ball velocity
  \ param krate current kick rate
  \ param ball_vel current ball velocity
  \ return maximum velocity for the target angle
 """


def calc_max_velocity(target_angle: AngleDeg,
                      krate,
                      ball_vel: Vector2D):
    ball_speed_max2 = pow(ServerParam.i().ball_speed_max(), 2)
    max_accel = min(ServerParam.i().max_power() * krate,
                    ServerParam.i().ball_accel_max())

    desired_ray = Ray2D(Vector2D(0.0, 0.0), target_angle)
    next_reachable_circle = Circle2D(ball_vel, max_accel)

    num = next_reachable_circle.intersection(desired_ray)
    vel1 = num[1]
    vel2 = num[2]
    if num[0] == 0:
        return Vector2D(0.0, 0.0)

    if num[0] == 1:
        if vel1.r2() > ball_speed_max2:
            # next inertia ball point is within reachable circle.
            if next_reachable_circle.contains(Vector2D(0.0, 0.0)):
                # can adjust angle at least
                vel1.setLength(ServerParam.i().ball_speed_max())

            else:
                # failed
                vel1.assign(0.0, 0.0)

        return vel1

    #
    # num == 2
    #   ball reachable circle does not contain the current ball pos.

    length1 = vel1.r2()
    length2 = vel2.r2()

    if length1 < length2:
        vel1, vel2 = vel2, vel1
        length1, length2 = length2, length1

    if length1 > ball_speed_max2:
        if length2 > ball_speed_max2:
            # failed
            vel1.assign(0.0, 0.0)

        else:
            vel1.setLength(ServerParam.i().ball_speed_max())

    return vel1
