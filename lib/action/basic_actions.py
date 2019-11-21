"""
  \ file basic_actions.py
  \ brief basic player actions
"""

from lib.player.soccer_action import *
from lib.player.templates import PlayerAgent
from lib.math.soccer_math import *
from lib.rcsc.server_param import ServerParam

"""
  \ class Body_TurnToPoint
  \ brief turn only body to point
"""


class TurnToPoint:
    def __init__(self, point: Vector2D, cycle: int = 1):
        self._point = point
        self._cycle = cycle

    def execute(self, agent: PlayerAgent):
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

    def execute(self, agent: PlayerAgent):
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

    def execute(self, agent: PlayerAgent):
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

    def execute(self, agent: PlayerAgent):
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


"""
  \ class Neck_TurnToRelative
  \ brief turn neck to the angle relative to body
"""


class Neck_TurnToRelative(NeckAction):
    def __init__(self, rel_angle: AngleDeg, NeckActions: list):
        super().__init__(NeckActions)
        self._rel_angle = rel_angle

    def execute(self, agent: PlayerAgent):
        return agent.do_turn_neck(self._rel_angle - agent.world().self().neck())


"""
  \ class Neck_TurnToPoint
  \ brief turn only neck to point
"""


class Neck_TurnToPoint(NeckAction):  # TODO : effector
    def __init__(self, points, NeckActions: list):
        super().__init__(NeckActions)
        self._points = points

    # def execute(self, agent: PlayerAgent):
    #     next_pos = agent.effector().queuedNextSelfPos()
    #     next_body = agent.effector().queuedNextSelfBody()
    #     next_view_width = agent.effector().queuedNextViewWidth().width() * 0.5
    #
    #     for p in self._points
    #         rel_pos = *p - next_pos
    #         rel_angle = rel_pos.th() - next_body
    #
    #         if rel_angle.abs() < ServerParam.i().maxNeckAngle() + next_view_width - 5.0:
    #             return agent.doTurnNeck(rel_angle - agent.world().self().neck())
    #
    #     return True


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

    def execute(self, agent: PlayerAgent):
        if agent.world().self().arm_movable() > 0:
            return False
        return agent.doPointtoOff()
