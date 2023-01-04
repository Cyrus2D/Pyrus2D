# from lib.player.player_agent import *
from lib.rcsc.server_param import ServerParam as SP
import pyrusgeom.soccer_math as smath
from pyrusgeom.geom_2d import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    
class GoToPoint:
    _dir_thr: float

    def __init__(self, target, dist_thr, max_dash_power, dash_speed=-1.0, cycle=100, save_recovery=True, dir_thr=15.0):
        self._target = target
        self._dist_thr = dist_thr
        self._max_dash_power = max_dash_power
        self._dash_speed = dash_speed
        self._cycle = cycle
        self._save_recovery = save_recovery
        self._dir_thr = dir_thr
        self._back_mode = False

    def execute(self, agent):
        if math.fabs(self._max_dash_power) < 0.1 or math.fabs(self._dash_speed) < 0.01:
            agent.do_turn(0)
            return True

        wm: 'WorldModel' = agent.world()
        inertia_point: Vector2D = wm.self().inertia_point(self._cycle)
        target_rel: Vector2D = self._target - inertia_point

        target_dist = target_rel.r()
        if target_dist < self._dist_thr:
            agent.do_turn(0.0)
            return False

        self.check_collision(agent)

        if self.do_turn(agent):
            return True

        if self.do_dash(agent):
            return True

        agent.do_turn(0)
        return False

    def do_turn(self, agent):
        wm: 'WorldModel' = agent.world()

        inertia_pos: Vector2D = wm.self().inertia_point(self._cycle)
        target_rel: Vector2D = self._target - inertia_pos
        target_dist = target_rel.r()
        max_turn = wm.self().player_type().effective_turn(SP.i().max_moment(), wm.self().vel().r())
        turn_moment: AngleDeg = target_rel.th() - wm.self().body()
        if turn_moment.abs() > max_turn and turn_moment.abs() > 90.0 and target_dist < 2.0 and wm.self().stamina_model().stamina() > SP.i().recover_dec_thr_value() + 500.0:
            effective_power = SP.i().max_dash_power() * wm.self().dash_rate()
            effective_back_power = SP.i().min_dash_power() * wm.self().dash_rate()
            if math.fabs(effective_back_power) > math.fabs(effective_power) * 0.75:
                self._back_mode = True
                turn_moment += 180.0

        turn_thr = 180.0
        if self._dist_thr < target_dist:
            turn_thr = AngleDeg.asin_deg(self._dist_thr / target_dist)
        turn_thr = max(self._dir_thr, turn_thr)

        if turn_moment.abs() < turn_thr:
            return False
        return agent.do_turn(turn_moment)

    def do_dash(self, agent):
        wm: 'WorldModel' = agent.world()

        inertia_pos: Vector2D = wm.self().inertia_point(self._cycle)
        target_rel: Vector2D = self._target - inertia_pos

        accel_angle: AngleDeg = wm.self().body()
        if self._back_mode:
            accel_angle += 180.0

        target_rel.rotate(-accel_angle)
        first_speed = smath.calc_first_term_geom_series(target_rel.x(), wm.self().player_type().player_decay(),
                                                        self._cycle)
        first_speed = smath.bound(- wm.self().player_type().player_speed_max(), first_speed,
                                  wm.self().player_type().player_speed_max())
        if self._dash_speed > 0.0:
            if first_speed > 0.0:
                first_speed = min(first_speed, self._dash_speed)
            else:
                first_speed = max(first_speed, -self._dash_speed)
        rel_vel = wm.self().vel()
        rel_vel.rotate(-accel_angle)
        required_accel = first_speed - rel_vel.x()
        if math.fabs(required_accel) < 0.05:
            return False
        dash_power = required_accel / wm.self().dash_rate()
        dash_power = min(dash_power, self._max_dash_power)
        if self._back_mode:
            dash_power = -dash_power
        dash_power = SP.i().normalize_dash_power(dash_power)
        # TODO check stamina check for save recovery
        return agent.do_dash(dash_power)

    def check_collision(self, agent):
        wm: 'WorldModel' = agent.world()

        collision_dist = wm.self().player_type().player_size() + SP.i().goal_post_radius() + 0.2

        goal_post_l = Vector2D(-SP.i().pitch_half_length() + SP.i().goal_post_radius(),
                               -SP.i().goal_half_width() - SP.i().goal_post_radius())
        goal_post_r = Vector2D(-SP.i().pitch_half_length() + SP.i().goal_post_radius(),
                               +SP.i().goal_half_width() + SP.i().goal_post_radius())

        dist_post_l = wm.self().pos().dist2(goal_post_l)
        dist_post_r = wm.self().pos().dist2(goal_post_r)

        nearest_post = goal_post_l
        if dist_post_l > dist_post_r:
            nearest_post = goal_post_r

        dist_post = min(dist_post_l, dist_post_r)
        if dist_post > collision_dist + wm.self().player_type().real_speed_max() + 0.5:
            return

        post_circle = Circle2D(nearest_post, collision_dist)
        move_line = Segment2D(wm.self().pos(), self._target)
        if len(post_circle.intersection(move_line)) == 0:
            return

        post_angle: AngleDeg = AngleDeg((nearest_post - wm.self().pos()).th())
        new_target: Vector2D = nearest_post

        if post_angle.is_left_of(wm.self().body()):
            new_target += Vector2D.from_polar(collision_dist + 0.1, post_angle + 90.0)
        else:
            new_target += Vector2D.from_polar(collision_dist + 0.1, post_angle - 90.0)

        self._target = new_target
