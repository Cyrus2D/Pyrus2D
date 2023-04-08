"""
  \ file kick_table.py
  \ brief kick table class File to generate smart kick.
"""
import functools

from lib.debug.debug import log
# from typing import List
# from enum import Enum

from lib.debug.level import Level
from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam
from pyrusgeom.soccer_math import *
from pyrusgeom.ray_2d import Ray2D
from pyrusgeom.circle_2d import Circle2D
from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.rect_2d import Rect2D
from pyrusgeom.size_2d import Size2D
from pyrusgeom.math_values import EPSILON
from lib.rcsc.game_time import *


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    

"""
      \ brief compare operation function
      \ param item1 left hand side variable
      \ param item2 right hand side variable
      \ return compared result
"""


def table_cmp(item1, item2) -> bool:
    if item1.max_speed_ == item2.max_speed_:
        return item1.power_ < item2.power_

    return item1.max_speed_ > item2.max_speed_


def sequence_cmp(item1, item2) -> bool:
    return item1.score_ > item2.score_


"""
  \ enum Flag
  \ brief status bit flags
"""

# class Flag(Enum):
SAFETY: hex = 0x0000
NEXT_TACKLEABLE: hex = 0x0001
NEXT_KICKABLE: hex = 0x0002
TACKLEABLE: hex = 0x0004
KICKABLE: hex = 0x0008
SELF_COLLISION: hex = 0x0010
RELEASE_INTERFERE: hex = 0x0020
MAYBE_RELEASE_INTERFERE: hex = 0x0040
OUT_OF_PITCH: hex = 0x0080
KICK_MISS_POSSIBILITY: hex = 0x0100
NOT_SAFETY: hex = 0xffff
NOT_NEXT_TACKLEABLE: hex = 0xfffe
NOT_NEXT_KICKABLE: hex = 0xfffd
NOT_TACKLEABLE: hex = 0xfffb
NOT_KICKABLE: hex = 0xfff7
NOT_SELF_COLLISION: hex = 0xffef
NOT_RELEASE_INTERFERE: hex = 0xffdf
NOT_MAYBE_RELEASE_INTERFERE: hex = 0xffbf
NOT_OUT_OF_PITCH: hex = 0xff7f
NOT_KICK_MISS_POSSIBILITY: hex = 0xfeff

NEAR_SIDE_RATE = 0.3  # < kickable margin rate for the near side sub-target
MID_RATE = 0.5  # < kickable margin rate for the middle distance sub-target
FAR_SIDE_RATE = 0.7  # < kickable margin rate for the far side sub-target
MAX_DEPTH = 2
STATE_DIVS_NEAR = 8
STATE_DIVS_MID = 12
STATE_DIVS_FAR = 15
# STATE_DIVS_NEAR = 4
# STATE_DIVS_MID = 8
# STATE_DIVS_FAR = 8
NUM_STATE = STATE_DIVS_NEAR + STATE_DIVS_MID + STATE_DIVS_FAR

DEST_DIR_DIVS: int = 72  # step: 5 degree

MAX_TABLE_SIZE: int = 128

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
            self.pos_ = Vector2D(0, 0)
            self.kick_rate_ = 0.0
            self.flag_ = NOT_SAFETY
        else:
            self.index_: int = args[0]
            self.dist_: float = args[1]
            self.pos_: Vector2D = args[2].copy()
            self.kick_rate_: float = args[3]
            self.flag_ = SAFETY


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

    def __init__(self, origin=0, destination=0):
        self.origin_ = origin
        self.dest_ = destination
        self.max_speed_ = 0.0
        self.power_ = 1000.0

    def __gt__(self, other):
        if self.max_speed_ == other.max_speed_:
            return self.power_ < other.power_

        return self.max_speed_ > other.max_speed_

    def copy(self):
        return Path(self.origin_, self.dest_)


"""
  \ class Sequence
  \ brief simulated kick sequence
 """


class Sequence:
    # < safety level flags. usually the combination of State flags
    # < ball positions
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
            self.speed_ = args[0].speed_.copy()
            self.power_ = args[0].power_.copy()
            self.score_ = args[0].score_

    def __repr__(self):
        return "[{} Step, next_pos = {}, speed = {}, pos_list = {}, flag = {}, score [{}]]".format(
            len(self.pos_list_), self.pos_list_[0], self.speed_, self.pos_list_, self.flag_, self.score_)


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
    ball_speed_max2 = ServerParam.i().ball_speed_max() ** 2
    max_accel = min(ServerParam.i().max_power() * krate,
                    ServerParam.i().ball_accel_max())

    desired_ray = Ray2D(Vector2D(0.0, 0.0), target_angle)
    next_reachable_circle = Circle2D(ball_vel, max_accel)

    num = next_reachable_circle.intersection(desired_ray)
    if len(num) == 0:
        return Vector2D(0.0, 0.0)
    
    vel1 = num[0]
    
    if len(num) == 1:
        if vel1.r2() > ball_speed_max2:
            # next inertia ball point is within reachable circle.
            if next_reachable_circle.contains(Vector2D(0.0, 0.0)):
                # can adjust angle at least
                vel1.set_length(ServerParam.i().ball_speed_max())

            else:
                # failed
                vel1.assign(0.0, 0.0)

        return vel1

    vel2 = num[1]
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
            vel1.set_length(ServerParam.i().ball_speed_max())

    return vel1


class _KickTable:
    debug_print_DEBUG: bool = False  # debug_prints IN KICKTABLE

    def __init__(self):
        self._old_player_type_id = -1
        self._player_size = 0.0
        self._kickable_margin = 0.0
        self._ball_size = 0.0
        self._state_cache = []
        for i in range(MAX_DEPTH):
            self._state_cache.append([])
            for j in range(NUM_STATE):
                self._state_cache[i].append(0.0)
        # not  static state list
        self._state_list = []
        self._tables = []

        self._current_state = State()

        self._state_cache = [[State()]] * DEST_DIR_DIVS

        self._candidates = []  # :  list[Sequence] = []

    """
    \ brief create heuristic table
    \ return result of table creation
    """

    def create_tables(self, player_type: PlayerType):
        if player_type.id() == self._old_player_type_id:
            return
        self._old_player_type_id = player_type.id()
        player_type = PlayerType()  # default type

        if (math.fabs(self._player_size - player_type.player_size()) < EPS
                and math.fabs(self._kickable_margin - player_type.kickable_margin()) < EPS
                and math.fabs(self._ball_size - ServerParam.i().ball_size()) < EPS):
            return False
        self._player_size = player_type.player_size()
        self._kickable_margin = player_type.kickable_margin()
        self._ball_size = ServerParam.i().ball_size()

        self.create_state_list(player_type)

        angle_step = 360.0 / DEST_DIR_DIVS
        angles = [AngleDeg(-180 + i * angle_step) for i in range(DEST_DIR_DIVS)]
        # TODO this functions should be checked
        from multiprocessing import Pool
        pool = Pool(4)
        self._tables = pool.map(self.create_table, angles)

        # for i in range(len(angles)):
        #     self._tables.append(self.create_table(angles[i]))
        return True

    """
      \ brief create static state list
    """

    def create_state_list(self, player_type: PlayerType):
        near_dist = calc_near_dist(player_type)
        mid_dist = calc_mid_dist(player_type)
        far_dist = calc_far_dist(player_type)

        near_angle_step = 360.0 / STATE_DIVS_NEAR
        mid_angle_step = 360.0 / STATE_DIVS_MID
        far_angle_step = 360.0 / STATE_DIVS_FAR

        index = 0
        self._state_list.clear()

        for near in range(STATE_DIVS_NEAR):
            angle = AngleDeg(-180.0 + (near_angle_step * near))
            pos = Vector2D.polar2vector(near_dist, angle)
            krate = player_type.kick_rate(near_dist, angle.degree())
            self._state_list.append(State(index, near_dist, pos, krate))
            index += 1

        for mid in range(STATE_DIVS_MID):
            angle = AngleDeg(-180.0 + (mid_angle_step * mid))
            pos = Vector2D.polar2vector(mid_dist, angle)
            krate = player_type.kick_rate(mid_dist, angle.degree())
            self._state_list.append(State(index, mid_dist, pos, krate))
            index += 1

        for far in range(STATE_DIVS_FAR):
            angle = AngleDeg(-180.0 + (far_angle_step * far))
            pos = Vector2D.polar2vector(far_dist, angle)
            krate = player_type.kick_rate(far_dist, angle.degree())
            self._state_list.append(State(index, far_dist, pos, krate))
            index += 1

    """
      \ brief create table for angle
      \ param angle target angle relative to body angle
      \ param table reference to the container variable
     """

    def create_table(self, angle: AngleDeg):
        # max_combination = NUM_STATE * NUM_STATE
        res: list = [None] * (NUM_STATE * NUM_STATE)
        max_state = len(self._state_list)

        for origin in range(max_state):
            for dest in range(max_state):
                vel = self._state_list[dest].pos_ - self._state_list[origin].pos_
                max_vel = calc_max_velocity(angle,
                                            self._state_list[dest].kick_rate_,
                                            vel)
                accel = max_vel - vel
                path = Path(origin, dest)
                path.max_speed_ = max_vel.r()
                path.power_ = accel.r() / self._state_list[dest].kick_rate_
                res[max_state * origin + dest] = path
        res.sort(key=functools.cmp_to_key(table_cmp))
        if len(res) > MAX_TABLE_SIZE:
            res = res[:MAX_TABLE_SIZE + 1]
        return res


    """
      \ brief update internal state
      \ param world  reference to the WorldModel
     """

    def update_state(self, world: 'WorldModel'):

        if KickTable.S_UPDATE_TIME == world.time():
            return

        KickTable.S_UPDATE_TIME = world.time().copy()

        self.create_state_cache(world)

    """
      \ brief implementation of the state update
      \ param world  reference to the WorldModel
     """

    def create_state_cache(self, world: 'WorldModel'):

        param = ServerParam.i()
        pitch = Rect2D(Vector2D(- param.pitch_half_length(), - param.pitch_half_width()), Size2D(param.pitch_length(),
                                                                                                 param.pitch_width()))
        self_type = world.self().player_type()
        near_dist = calc_near_dist(self_type)
        mid_dist = calc_mid_dist(self_type)
        far_dist = calc_far_dist(self_type)

        rpos = world.ball().rpos()
        rpos.rotate(- world.self().body())

        dist = rpos.r()
        angle = rpos.th()

        if math.fabs(dist - near_dist) < math.fabs(dist - far_dist):
            dir_div = STATE_DIVS_NEAR
        else:
            dir_div = STATE_DIVS_FAR

        self._current_state.index_ = (round(dir_div * round(angle.degree() + 180.0) / 360.0))
        if self._current_state.index_ >= dir_div:
            self._current_state.index_ = 0

        # self._current_state.pos_ = world.ball().rpos()
        self._current_state.pos_ = world.ball().pos()
        self._current_state.kick_rate_ = world.self().kick_rate()

        self.check_interfere_at(world, self._current_state)  # 0

        #
        # create future state
        #

        self_pos = world.self().pos()
        self_vel = world.self().vel()

        for i in range(MAX_DEPTH):
            self._state_cache[i].clear()

            self_pos += self_vel
            self_vel *= self_type.player_decay()

            index = 0
            for near in range(STATE_DIVS_NEAR):
                pos = self._state_list[index].pos_.copy()
                krate = self_type.kick_rate(near_dist, pos.th().degree())

                pos.rotate(world.self().body())
                pos.set_length(near_dist)
                pos += self_pos
                self._state_cache[i].append(State(index, near_dist, pos, krate))
                self.check_interfere_at(world, self._state_cache[i][-1])  # i + 1
                if not pitch.contains(pos):
                    self._state_cache[i][-1].flag_ |= OUT_OF_PITCH

                index += 1

            for mid in range(STATE_DIVS_MID):
                pos = self._state_list[index].pos_.copy()
                krate = self_type.kick_rate(mid_dist, pos.th().degree())

                pos.rotate(world.self().body())
                pos.set_length(mid_dist)
                pos += self_pos

                self._state_cache[i].append(State(index, mid_dist, pos, krate))
                self.check_interfere_at(world, self._state_cache[i][-1])  # i + 1
                if not pitch.contains(pos):
                    self._state_cache[i][-1].flag_ |= OUT_OF_PITCH

                index += 1

            for far in range(STATE_DIVS_FAR):
                pos = self._state_list[index].pos_.copy()
                krate = self_type.kick_rate(far_dist, pos.th().degree())

                pos.rotate(world.self().body())
                pos.set_length(far_dist)
                pos += self_pos

                self._state_cache[i].append(State(index, far_dist, pos, krate))
                self.check_interfere_at(world, self._state_cache[i][-1])  # i + 1
                if not pitch.contains(pos):
                    self._state_cache[i][-1].flag_ |= OUT_OF_PITCH

                index += 1

    """
      \ brief update collision flag of state caches for the target_point and first_speed
      \ param world  reference to the WorldModel
      \ param target_point kick target point
      \ param first_speed required first speed
     """

    def check_collision_after_release(self, world: 'WorldModel', target_point: Vector2D, first_speed):

        self_type = world.self().player_type()

        collide_dist2 = pow(self_type.player_size() + ServerParam.i().ball_size(), 2)

        self_pos = world.self().pos()
        self_vel = world.self().vel()

        # check the release kick from current state

        self_pos += self_vel
        self_vel *= self_type.player_decay()

        release_pos = (target_point - self._current_state.pos_)
        release_pos.set_length(first_speed)

        if self_pos.dist2(release_pos) < collide_dist2:

            self._current_state.flag_ |= SELF_COLLISION

        else:
            self._current_state.flag_ &= NOT_SELF_COLLISION

        # check the release kick from future state

        for i in range(MAX_DEPTH):
            self_pos += self_vel
            self_vel *= self_type.player_decay()

            for it in self._state_cache[i]:
                release_pos = (target_point - it.pos_)
                release_pos.set_length(first_speed)

                if self_pos.dist2(release_pos) < collide_dist2:

                    it.flag_ |= SELF_COLLISION
                else:
                    it.flag_ &= NOT_SELF_COLLISION

    """
      \ brief update interfere level at state   
      \ param world  reference to the WorldModel
      \ param cycle the cycle delay for state
      \ param state reference to the State variable to be updated
    """

    @staticmethod
    def check_interfere_at(world: 'WorldModel',
                           # cycle,  # not needed
                           state: State):
        # cycle += 0  Check need
        penalty_area = Rect2D(Vector2D(ServerParam.i().their_penalty_area_line_x(),
                                       - ServerParam.i().penalty_area_half_width()),
                              Size2D(ServerParam.i().penalty_area_length(),
                                     ServerParam.i().penalty_area_width()))
        flag = SAFETY
        OFB = world.opponents_from_ball()
        if len(OFB) == 0:
            state.flag_ = SAFETY
            return
        for o in OFB:
            if o is None or o.player_type() is None:
                continue
            if o.pos_count() >= 8:
                continue
            if o.is_ghost():
                continue
            if o.dist_from_ball() > 10.0:
                break

            opp_next = o.pos() + o.vel()
            opp_dist = opp_next.dist(state.pos_)

            if o.is_tackling():
                if opp_dist < (o.playerTypePtr().player_size()
                               + ServerParam.i().ball_size()):
                    flag |= KICKABLE
                    break

                continue

            control_area = o.player_type().catchable_area() if (
                    o.goalie() and penalty_area.contains(o.pos()) and penalty_area.contains(state.pos_
                                                                                            )) else o.player_type().kickable_area()

            #
            # check kick possibility
            #
            if not o.is_ghost() and o.pos_count() <= 2 and opp_dist < control_area + 0.15:
                flag |= KICKABLE
                break

            opp_body = o.body() if o.body_count() <= 1 else (state.pos_ - opp_next).th()
            player_2_pos = Vector2D(state.pos_ - opp_next)
            player_2_pos.rotate(- opp_body)
            #
            # check tackle possibility
            #
            tackle_dist = ServerParam.i().tackle_dist() if player_2_pos.x() > 0.0 else ServerParam.i().tackle_back_dist()
            if tackle_dist > EPSILON:
                tackle_prob = (pow(player_2_pos.abs_x() / tackle_dist,
                                   ServerParam.i().tackle_exponent()) + pow(
                    player_2_pos.abs_y() / ServerParam.i().tackle_width(),
                    ServerParam.i().tackle_exponent()))
                if tackle_prob < 1.0 and 1.0 - tackle_prob > 0.7:  # success probability
                    flag |= TACKLEABLE

                    # check kick or tackle possibility after dash

            player_type = o.player_type()
            max_accel = (ServerParam.i().max_dash_power()
                         * player_type.dash_power_rate()
                         * player_type.effort_max())

            if player_2_pos.abs_y() < control_area and (
                    player_2_pos.abs_x() < max_accel or (player_2_pos + Vector2D(max_accel, 0.0)).r() < control_area or (
                    player_2_pos - Vector2D(max_accel, 0.0)).r() < control_area):
                flag |= NEXT_KICKABLE
            elif (player_2_pos.abs_y() < ServerParam.i().tackle_width() * 0.7
                  and player_2_pos.x() > 0.0
                  and player_2_pos.x() - max_accel < ServerParam.i().tackle_dist() - 0.3):
                flag |= NEXT_TACKLEABLE

        state.flag_ = flag

    """
      \ brief update interfere level after release kick for all states
      \ param world  reference to the WorldModel
      \ param target_point kick target point
      \ param first_speed required first speed
      \ brief update interfere level after release kick for each state
      \ param world  reference to the WorldModel
      \ param target_point kick target point
      \ param first_speed required first speed
      \ param cycle the cycle delay for state
      \ param state reference to the State variable to be updated
    """

    def check_interfere_after_release(self, *args):  # , **kwargs):):
        if len(args) == 3:
            world: 'WorldModel' = args[0]
            target_point: Vector2D = args[1]
            first_speed: float = args[2]
            self.check_interfere_after_release(world, target_point, first_speed, 1, self._current_state)

            for i in range(MAX_DEPTH):
                for state in self._state_cache[i]:
                    state.flag_ &= NOT_RELEASE_INTERFERE
                    state.flag_ &= NOT_MAYBE_RELEASE_INTERFERE

                    self.check_interfere_after_release(world, target_point, first_speed, i + 2, state)
        elif len(args) == 5:
            world: 'WorldModel' = args[0]
            target_point: Vector2D = args[1]
            first_speed: float = args[2]
            cycle: int = args[3]
            state: State = args[4]

            penalty_area = Rect2D(Vector2D(ServerParam.i().their_penalty_area_line_x(),
                                           - ServerParam.i().penalty_area_half_width()),
                                  Size2D(ServerParam.i().penalty_area_length(),
                                         ServerParam.i().penalty_area_width()))

            ball_pos = target_point - state.pos_
            ball_pos.set_length(first_speed)
            ball_pos += state.pos_

            OFB = world.opponents_from_ball()
            if len(OFB) == 0:
                state.flag_ = SAFETY
                return
            for o in OFB:
                if o is None or o.player_type() is None:
                    continue
                if o.pos_count() >= 8:
                    continue
                if o.is_ghost():
                    continue
                if o.dist_from_ball() > 10.0:
                    break
                opp_pos = o.inertia_point(cycle)
                if not opp_pos.is_valid():
                    opp_pos = o.pos() + o.vel()

                if o.is_tackling():
                    if opp_pos.dist(ball_pos) < (o.player_type().player_size() + ServerParam.i().ball_size()):
                        state.flag_ |= RELEASE_INTERFERE
                    continue
                control_area = o.player_type().catchable_area() if (
                        o.goalie() and penalty_area.contains(o.pos()) and penalty_area.contains(
                    state.pos_)) else o.player_type().kickable_area()

                control_area += 0.1
                control_area2 = pow(control_area, 2)

                if ball_pos.dist2(opp_pos) < control_area2:
                    if cycle <= 1:
                        state.flag_ |= RELEASE_INTERFERE

                    else:
                        state.flag_ |= RELEASE_INTERFERE
                else:  # if  cycle <= 1 :
                    opp_body = o.body() if o.body_count() <= 1 else (ball_pos - opp_pos).th()
                    player_2_pos = ball_pos - opp_pos
                    player_2_pos.rotate(- opp_body)

                    tackle_dist = ServerParam.i().tackle_dist() if player_2_pos.x() > 0.0 else ServerParam.i().tackle_back_dist()
                    if tackle_dist > EPSILON:
                        tackle_prob = (pow(player_2_pos.abs_x() / tackle_dist,
                                           ServerParam.i().tackle_exponent()) + pow(
                            player_2_pos.abs_y() / ServerParam.i().tackle_width(),
                            ServerParam.i().tackle_exponent()))
                        if tackle_prob < 1.0 and 1.0 - tackle_prob > 0.8:  # success probability
                            state.flag_ |= MAYBE_RELEASE_INTERFERE
                    player_type = o.player_type()
                    max_accel = (ServerParam.i().max_dash_power()
                                 * player_type.dash_power_rate()
                                 * player_type.effort_max()) * 0.8
                    if (player_2_pos.abs_y() < control_area - 0.1
                            and (player_2_pos.abs_x() < max_accel
                                 or (player_2_pos + Vector2D(max_accel, 0.0)).r() < control_area - 0.25
                                 or (player_2_pos - Vector2D(max_accel, 0.0)).r() < control_area - 0.25)):
                        state.flag_ |= MAYBE_RELEASE_INTERFERE

                    elif (player_2_pos.abs_y() < ServerParam.i().tackle_width() * 0.7
                          and player_2_pos.x() - max_accel < ServerParam.i().tackle_dist() - 0.5):
                        state.flag_ |= MAYBE_RELEASE_INTERFERE

    """
      \ brief simulate one step kick
      \ param world  reference to the WorldModel
      \ param target_point kick target point
      \ param first_speed required first speed
     """

    def simulate_one_step(self, world: 'WorldModel', target_point: Vector2D, first_speed):
        if self._current_state.flag_ & SELF_COLLISION:
            return False

        if self._current_state.flag_ & RELEASE_INTERFERE:
            return False

        current_max_accel = min(self._current_state.kick_rate_ * ServerParam.i().max_power(),
                                ServerParam.i().ball_accel_max())
        target_vel = (target_point - world.ball().pos())
        target_vel.set_length(first_speed)

        accel = target_vel - world.ball().vel()
        accel_r = accel.r()
        if accel_r > current_max_accel:
            max_vel = calc_max_velocity(target_vel.th(),
                                        self._current_state.kick_rate_,
                                        world.ball().vel())
            accel = max_vel - world.ball().vel()
            self._candidates.append(Sequence())
            self._candidates[-1].flag_ = self._current_state.flag_
            self._candidates[-1].pos_list_.append(world.ball().pos() + max_vel)
            self._candidates[-1].speed_ = max_vel.r()
            self._candidates[-1].power_ = accel.r() / self._current_state.kick_rate_
            return False

        self._candidates.append(Sequence())
        self._candidates[-1].flag_ = self._current_state.flag_
        self._candidates[-1].pos_list_.append(world.ball().pos() + target_vel)
        self._candidates[-1].speed_ = first_speed
        self._candidates[-1].power_ = accel_r / self._current_state.kick_rate_
        """
            dlog.addText( Logger.KICK,
                          "ok__ 1 step: target_vel=(%.2f %.2f)%.3f required_accel=%.3f < max_accel=%.3f"
                          " kick_rate=%f power=%.1f",
                          target_vel.x, target_vel.y,
                          first_speed,
                          accel_r,
                          current_max_accel,
                          self._current_state.kick_rate_,
                          self._candidates[-1].power_ )
        """
        return True

    """
      \ brief simulate two step kicks
      \ param world  reference to the WorldModel
      \ param target_point kick target point
      \ param first_speed required first speed
     """

    def simulate_two_step(self, world: 'WorldModel', target_point: Vector2D, first_speed):
        max_power = ServerParam.i().max_power()
        accel_max = ServerParam.i().ball_accel_max()
        ball_decay = ServerParam.i().ball_decay()

        self_type = world.self().player_type()

        current_max_accel = min(self._current_state.kick_rate_ * max_power, accel_max)

        param = ServerParam.i()
        my_kickable_area = self_type.kickable_area()

        my_noise = world.self().vel().r() * param.player_rand()
        current_dir_diff_rate = (world.ball().angle_from_self() - world.self().body()).abs() / 180.0

        current_dist_rate = ((world.ball().dist_from_self()
                              - self_type.player_size()
                              - param.ball_size())
                             / self_type.kickable_margin())
        current_pos_rate = 0.5 + 0.25 * (current_dir_diff_rate + current_dist_rate)

        current_speed_rate = 0.5 + 0.5 * (world.ball().vel().r() / (
                param.ball_speed_max() * param.default_player_decay()))
        # my_final_pos = world.self().pos() + world.self().vel() + world.self().vel() * self_type.player_decay()

        success_count = 0
        max_speed2 = 0.0
        for i in range(NUM_STATE):
            state = self._state_cache[0][i]

            if state.flag_ & OUT_OF_PITCH:
                continue

            if state.flag_ & KICKABLE:
                continue

            if state.flag_ & SELF_COLLISION:
                continue

            if state.flag_ & RELEASE_INTERFERE:
                return False

            kick_miss_flag = SAFETY
            target_vel = (target_point - state.pos_).set_length_vector(first_speed)

            vel = state.pos_ - world.ball().pos()
            accel = vel - world.ball().vel()
            accel_r = accel.r()

            if accel_r > current_max_accel:
                continue
            kick_power = accel_r / world.self().kick_rate()
            ball_noise = vel.r() * param.ball_rand()
            max_kick_rand = self_type.kick_rand() * (kick_power / param.max_power()) * (
                    current_pos_rate + current_speed_rate)
            if ((my_noise + ball_noise + max_kick_rand)  # * 0.9
                    > my_kickable_area - state.dist_ - 0.05):  # 0.1 )
                kick_miss_flag |= KICK_MISS_POSSIBILITY

            vel *= ball_decay
            accel = target_vel - vel
            accel_r = accel.r()

            if accel_r > min(state.kick_rate_ * max_power, accel_max):

                if success_count == 0:
                    max_vel = calc_max_velocity(target_vel.th(),
                                                state.kick_rate_,
                                                vel)
                    d2 = max_vel.r2()
                    if max_speed2 < d2:
                        if max_speed2 == 0.0:
                            self._candidates.append(Sequence())

                        max_speed2 = d2
                        accel = max_vel - vel
                        self._candidates[-1].flag_ = ((self._current_state.flag_ & NOT_RELEASE_INTERFERE)
                                                      | state.flag_)
                        self._candidates[-1].pos_list_.clear()
                        self._candidates[-1].pos_list_.append(state.pos_.copy())
                        self._candidates[-1].pos_list_.append(state.pos_ + max_vel)
                        self._candidates[-1].speed_ = math.sqrt(max_speed2)
                        self._candidates[-1].power_ = accel.r() / state.kick_rate_
                        success_count += 1
                continue
            self._candidates.append(Sequence())
            self._candidates[-1].flag_ = ((self._current_state.flag_ & NOT_RELEASE_INTERFERE)
                                          | state.flag_
                                          | kick_miss_flag)
            self._candidates[-1].pos_list_.append(state.pos_.copy())
            self._candidates[-1].pos_list_.append(state.pos_ + target_vel)
            self._candidates[-1].speed_ = first_speed
            self._candidates[-1].power_ = accel_r / state.kick_rate_
            success_count += 1
        return success_count > 0

    """
      \ brief simulate three step kicks
      \ param world  reference to the WorldModel
      \ param target_point kick target point
      \ param first_speed required first speed
     """

    def simulate_three_step(self, world: 'WorldModel',
                            target_point: Vector2D,
                            first_speed):

        max_power = ServerParam.i().max_power()
        accel_max = ServerParam.i().ball_accel_max()
        ball_decay = ServerParam.i().ball_decay()

        current_max_accel = min(self._current_state.kick_rate_ * max_power,
                                accel_max)
        current_max_accel2 = current_max_accel * current_max_accel

        param = ServerParam.i()

        self_type = world.self().player_type()

        my_kickable_area = self_type.kickable_area()

        my_noise1 = world.self().vel().r() * param.player_rand()
        current_dir_diff_rate = (world.ball().angle_from_self() - world.self().body()).abs() / 180.0
        current_dist_rate = ((world.ball().dist_from_self()
                              - self_type.player_size()
                              - param.ball_size())
                             / self_type.kickable_margin())
        current_pos_rate = 0.5 + 0.25 * (current_dir_diff_rate + current_dist_rate)
        current_speed_rate = 0.5 + 0.5 * (world.ball().vel().r()
                                          / (param.ball_speed_max() * param.ball_decay()))

        target_rel_angle = (target_point - world.self().pos()).th() - world.self().body()
        angle_deg = target_rel_angle.degree() + 180.0
        target_angle_index = round(DEST_DIR_DIVS * (angle_deg / 360.0))
        if target_angle_index >= DEST_DIR_DIVS:
            target_angle_index = 0

        table = self._tables[target_angle_index]

        success_count = 0
        max_speed2 = 0.0

        count = 0

        for it in table:
            if count > MAX_TABLE_SIZE:
                break
            if success_count > 10:
                break
            state_1st = self._state_cache[0][it.origin_]
            state_2nd = self._state_cache[1][it.dest_]

            if state_1st.flag_ & OUT_OF_PITCH:
                continue

            if state_2nd.flag_ & OUT_OF_PITCH:
                continue

            if state_1st.flag_ & KICKABLE:
                continue

            if state_2nd.flag_ & KICKABLE:
                continue

            if state_2nd.flag_ & SELF_COLLISION:
                continue

            if state_2nd.flag_ & RELEASE_INTERFERE:
                return False

            target_vel = (target_point - state_2nd.pos_).set_length_vector(first_speed)

            kick_miss_flag = SAFETY

            vel1 = state_1st.pos_ - world.ball().pos()
            accel = vel1 - world.ball().vel()
            accel_r2 = accel.r2()

            if accel_r2 > current_max_accel2:
                continue

            kick_power = math.sqrt(accel_r2) / world.self().kick_rate()
            ball_noise = vel1.r() * param.ball_rand()
            max_kick_rand = self_type.kick_rand() * (kick_power / param.max_power()) * (
                    current_pos_rate + current_speed_rate)

            if ((my_noise1 + ball_noise + max_kick_rand)  # * 0.95
                    > my_kickable_area - state_1st.dist_ - 0.05):  # 0.1 )
                kick_miss_flag |= KICK_MISS_POSSIBILITY

            vel1 *= ball_decay
            vel2 = state_2nd.pos_ - state_1st.pos_
            accel = vel2 - vel1
            accel_r2 = accel.r2()

            if accel_r2 > pow(min(state_1st.kick_rate_ * max_power, accel_max), 2):
                continue

            vel2 *= ball_decay

            accel = target_vel - vel2
            accel_r2 = accel.r2()
            if accel_r2 > pow(min(state_2nd.kick_rate_ * max_power, accel_max), 2):
                if success_count == 0:
                    max_vel = calc_max_velocity(target_vel.th(),
                                                state_2nd.kick_rate_,
                                                vel2)
                    d2 = max_vel.r2()
                    if max_speed2 < d2:
                        if max_speed2 == 0.0:
                            self._candidates.append(Sequence())

                        max_speed2 = d2
                        accel = max_vel - vel2

                        self._candidates[-1].flag_ = ((self._current_state.flag_ & NOT_RELEASE_INTERFERE)
                                                      | (state_1st.flag_ & NOT_RELEASE_INTERFERE)
                                                      | state_2nd.flag_)
                        self._candidates[-1].pos_list_.clear()
                        self._candidates[-1].pos_list_.append(state_1st.pos_.copy())
                        self._candidates[-1].pos_list_.append(state_2nd.pos_.copy())
                        self._candidates[-1].pos_list_.append(state_2nd.pos_ + max_vel)
                        self._candidates[-1].speed_ = math.sqrt(max_speed2)
                        self._candidates[-1].power_ = accel.r() / state_2nd.kick_rate_
                continue
            self._candidates.append(Sequence())
            self._candidates[-1].flag_ = ((self._current_state.flag_ & NOT_RELEASE_INTERFERE)
                                          | (state_1st.flag_ & NOT_RELEASE_INTERFERE)
                                          | state_2nd.flag_
                                          | kick_miss_flag)
            self._candidates[-1].pos_list_.append(state_1st.pos_.copy())
            self._candidates[-1].pos_list_.append(state_2nd.pos_.copy())
            self._candidates[-1].pos_list_.append(state_2nd.pos_ + target_vel)
            self._candidates[-1].speed_ = first_speed
            self._candidates[-1].power_ = math.sqrt(accel_r2) / state_2nd.kick_rate_
            success_count += 1
        return success_count > 0

    """
      \ brief evaluate candidate kick sequences
      \ param first_speed required first speed
      \ param allowable_speed required first speed threshold
     """

    def evaluate(self, first_speed, allowable_speed):
        power_thr1 = ServerParam.i().max_power() * 0.94
        power_thr2 = ServerParam.i().max_power() * 0.9
        for it in self._candidates:
            n_kick = len(it.pos_list_)

            it.score_ = 1000.0

            if it.speed_ < first_speed:
                if n_kick > 1 or it.speed_ < allowable_speed:
                    it.score_ = -10000.0
                    it.score_ -= (first_speed - it.speed_) * 100000.0

                else:
                    it.score_ -= 50.0

            if it.flag_ & TACKLEABLE:
                it.score_ -= 500.0

            if it.flag_ & NEXT_TACKLEABLE:
                it.score_ -= 300.0

            if it.flag_ & NEXT_KICKABLE:
                it.score_ -= 600.0

            if it.flag_ & MAYBE_RELEASE_INTERFERE:
                if n_kick == 1:
                    it.score_ -= 250.0

                else:
                    it.score_ -= 200.0

            if n_kick == 3:
                it.score_ -= 200.0

            elif n_kick == 2:
                it.score_ -= 50.0

            if n_kick > 1:
                if it.power_ > power_thr1:
                    it.score_ -= 75.0

                elif it.power_ > power_thr2:
                    it.score_ -= 25.0

            it.score_ -= it.power_ * 0.5

            if it.flag_ & KICK_MISS_POSSIBILITY:
                it.score_ -= 30.0

    """
    \ brief simulate kick sequence
    \ param world  reference to the WorldModel
    \ param target_point kick target point
    \ param first_speed required first speed
    \ param allowable_speed required first speed threshold
    \ param max_step maximum size of kick sequence
    \ param sequence reference to the result variable
    \ return if successful kick is found, True, False is returned but kick sequence is generated anyway.
    """

    def simulate(self, world, target_point: Vector2D, first_speed, allowable_speed, max_step, sequence: Sequence):

        if len(self._state_list) == 0:
            log.sw_log().kick().add_text( 'there isnt any state list')
            # if _KickTable.debug_print_DEBUG:
            #     debug_print("False , Len  == 0")
            return False

        target_speed = bound(0.0,
                             first_speed,
                             ServerParam.i().ball_speed_max())
        speed_thr = bound(0.0,
                          allowable_speed,
                          target_speed)

        self._candidates.clear()

        self.update_state(world)

        self.check_collision_after_release(world,
                                           target_point,
                                           target_speed)
        self.check_interfere_after_release(world,
                                           target_point,
                                           target_speed)

        if (max_step >= 1
                and self.simulate_one_step(world,
                                           target_point,
                                           target_speed)):
            if _KickTable.debug_print_DEBUG:
                log.sw_log().kick().add_text( "simulate() found 1 step")
        if (max_step >= 2
                and self.simulate_two_step(world,
                                           target_point,
                                           target_speed)):
            if _KickTable.debug_print_DEBUG:
                log.sw_log().kick().add_text( "simulate() found 2 step")
        if (max_step >= 3
                and self.simulate_three_step(world,
                                             target_point,
                                             target_speed)):
            if _KickTable.debug_print_DEBUG:
                log.sw_log().kick().add_text( "simulate() found 3 step")

        self.evaluate(target_speed, speed_thr)
        log.sw_log().kick().add_text( "candidate number:{}".format(len(self._candidates)))
        if not self._candidates:
            # if _KickTable.debug_print_DEBUG:
            #     debug_print("False -> candidates len == ", len(self._candidates))
            rtn_list = [False, sequence]
            return rtn_list
        sequence = max(self._candidates, key=functools.cmp_to_key(sequence_cmp))  # TODO : CMP Check
        if _KickTable.debug_print_DEBUG or True:
            for tmp in self._candidates:
                log.sw_log().kick().add_text(
                              f"simulate() result next_pos={sequence.pos_list_[0]}  flag={sequence.flag_} n_kick={len(sequence.pos_list_)} speed= {sequence.speed_} power={sequence.power_}  score={sequence.score_}")
            log.os_log().info(f"Smart kick : {sequence.speed_ >= target_speed - EPS} -> seq speed is {sequence.speed_} & tar speed eps is {target_speed - EPS}")
        rtn_list = [sequence.speed_ >= target_speed - EPS, sequence]
        return rtn_list

    """
    \ brief get the candidate kick sequences
    \ return  reference to the container of Sequence
    """

    def candidates(self):
        return self.candidates


"""
  \ brief singleton interface
  \ return reference to the singleton instance
 """


class KickTable:
    S_UPDATE_TIME = GameTime(-1, 0)

    _instance: _KickTable = _KickTable()

    @staticmethod
    def instance() -> _KickTable:
        return KickTable._instance
