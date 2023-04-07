"""
  \ file basic_actions.py
  \ brief basic player actions
"""
from lib.debug.debug import log
from lib.player.soccer_action import *
from pyrusgeom.soccer_math import *
from lib.rcsc.server_param import ServerParam
from pyrusgeom.angle_deg import AngleDeg


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent



"""
  \ class Body_TurnToPoint
  \ brief turn only body to point
"""

class TurnToPoint:
    def __init__(self, point: Vector2D, cycle: int = 1):
        self._point = point
        self._cycle = cycle

    def execute(self, agent: 'PlayerAgent'):
        me = agent.world().self()

        if not me.pos().is_valid():
            return agent.do_turn(60)

        my_point = me.inertia_point(self._cycle)
        target_rel_angle = (self._point - my_point).th() - me.body()

        agent.do_turn(target_rel_angle)
        if target_rel_angle.abs() < 1:
            return False
        return True


"""
   class Body_TurnToAngle
   brief align body angle to the target angle
"""


class TurnToAngle(BodyAction):
    def __init__(self, angle: AngleDeg):
        super().__init__()
        self._angle = angle

    def execute(self, agent: 'PlayerAgent'):
        me = agent.world().self()

        # if not me.faceValid(): TODO : fullstate
        #     agent.do_turn(0.0)
        #     return False

        agent.do_turn(self._angle - me.body())
        return True


"""
  \ class Body_TurnToBall
  \ brief turn only body to ball
"""


class TurnToBall(BodyAction):
    def __init__(self, cycle: int = 1):
        super().__init__()
        self._cycle = cycle

    def execute(self, agent: 'PlayerAgent'):
        if not agent.world().ball().posValid():
            return False

        ball_point = agent.world().ball().inertia_point(self._cycle)

        return TurnToPoint(ball_point, self._cycle).execute(agent)


"""
  \ class Body_TackleToPoint
  \ brief tackle ball to point
"""


class TackleToPoint(BodyAction):
    def __init__(self, point: Vector2D, min_prob: float = 0.5, min_speed: float = 0.0):
        super().__init__()
        self._point = point
        self._min_prob = min_prob
        self._min_speed = min_speed

    def execute(self, agent: 'PlayerAgent'):
        wm = agent.world()
        sp = ServerParam.i()

        if wm.self().tackle_probability() < self._min_prob:
            return False

        target_angle = (self._point - wm.ball().pos()).th()
        target_rel_angle = target_angle - wm.self().body()

        # if agent.config().version() < 12.0:
        #     if target_rel_angle.abs() < 90.0:
        #         return agent.do_tackle(sp.maxTacklePower())
        #     elif sp.maxBackTacklePower() > 0.0:
        #         # backward case
        #         return agent.do_tackle(- sp.maxBackTacklePower())
        #     return False

        ball_rel_angle = wm.ball().rpos().th() - wm.self().body()

        eff_power = sp.max_back_tackle_power() + (
                (sp.max_tackle_power() - sp.max_back_tackle_power()) * (1.0 - target_rel_angle.abs() / 180.0))
        eff_power *= sp.tackle_power_rate()
        eff_power *= 1.0 - 0.5 * (ball_rel_angle.abs() / 180.0)

        vel = wm.ball().vel() + Vector2D.polar2vector(eff_power, target_angle)

        if ((vel.th() - target_angle).abs() > 90.0  # never accelerate to the target direction
                or vel.r() < self._min_speed):  # too small speed
            return False

        return agent.do_tackle(target_rel_angle.degree(), True)  # TODO need Check


class SetFocusToPoint(FocusPointAction):
    def __init__(self, next_focus_point: Vector2D):
        super().__init__()
        self.next_focus_point: Vector2D = next_focus_point

    def execute(self, agent: 'PlayerAgent'):
        next_view_width = agent.effector().queued_next_view_width().width()
        my_next_pos = agent.effector().queued_next_self_pos()
        my_next_face = agent.effector().queued_next_self_face()
        current_focus_point_dist = agent.world().self().focus_point_dist()
        current_focus_point_dir = agent.world().self().focus_point_dir()
        current_focus_point_dir = AngleDeg(min_max(-next_view_width / 2.0, current_focus_point_dir.degree(), next_view_width / 2.0))
        next_focus_point_dist = my_next_pos.dist(self.next_focus_point)
        if not (0.0 < next_focus_point_dist < 40.0):
            log.os_log().info(f'(FocusToPoint execute) Next focus point dist should be 0<{next_focus_point_dist}<40')
        next_focus_point_dist = min_max(0.0, next_focus_point_dist, 40.0)
        change_focus_moment_dist = next_focus_point_dist - current_focus_point_dist

        original_next_focus_point_dir_to_pos = (self.next_focus_point - my_next_pos).th()
        next_focus_point_dir = (self.next_focus_point - my_next_pos).th() - my_next_face
        if not (-next_view_width / 2.0 < next_focus_point_dir.degree() < next_view_width / 2.0):
            log.os_log().info(f'(FocusToPoint execute) Next focus point dir should be {-next_view_width / 2.0}<{next_focus_point_dir.degree()}<{next_view_width/2.0}')
        next_focus_point_dir = AngleDeg(min_max(-next_view_width / 2.0, next_focus_point_dir.degree(), next_view_width / 2.0))
        if abs(next_focus_point_dir.abs() - next_view_width) / 2.0 < 0.001:
            positive = AngleDeg(next_view_width / 2.0) + my_next_face
            negative = AngleDeg(-next_view_width / 2.0) + my_next_face
            if (positive - original_next_focus_point_dir_to_pos).abs() < (negative - original_next_focus_point_dir_to_pos).abs():
                next_focus_point_dir = AngleDeg(next_view_width / 2.0)
            else:
                next_focus_point_dir = AngleDeg(-next_view_width / 2.0)
        change_focus_moment_dir = next_focus_point_dir - current_focus_point_dir
        return agent.do_change_focus(change_focus_moment_dist, change_focus_moment_dir)


class SetFocusToBall(FocusPointAction):
    def __init__(self):
        super().__init__()

    def execute(self, agent: 'PlayerAgent'):
        next_ball_pos = agent.effector().queued_next_ball_pos()
        return SetFocusToPoint(next_ball_pos).execute(agent)


class SetFocusToSelf(FocusPointAction):
    def __init__(self):
        super().__init__()

    def execute(self, agent: 'PlayerAgent'):
        next_self_pos = agent.effector().queued_next_self_pos()
        return SetFocusToPoint(next_self_pos).execute(agent)


class SetFocusToFlags(FocusPointAction):
    # TODO this one and others should be implemented
    pass

"""
  \ class Arm_Off
  \ brief turn off the pointing arm
"""


class ArmOff(ArmAction):
    """
      \ brief execute action
      \ param agent the agent itself
      \ return True if action is performed
    """

    def execute(self, agent: 'PlayerAgent'):
        if agent.world().self().arm_movable() > 0:
            return False
        return agent.doPointtoOff()
