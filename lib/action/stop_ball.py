"""
  \ file body_stop_ball.py
  \ brief kick the ball to keep a current positional relation.
"""
from lib.player.soccer_action import *
from lib.math.geom_2d import *

"""
  \ class Body_StopBall
  \ brief stop the ball, possible as.
"""


class StopBall(BodyAction):
    """
      \ brief accessible from global.
    """

    def __init__(self):
        super().__init__()

    """
      \ brief execute action
      \ param agent pointer to the agent itself
      \ return True if action is performed
    """

    def execute(self, agent: PlayerAgent):
        wm: WorldModel = agent.world()
        if not wm.self().isKickable():
            return False
        # if not wm.ball().velValid()   nice :)
        accel_radius = 0.0
        accel_angle = AngleDeg()

        # calcAccel(agent, accel_radius, accel_angle)

        if accel_radius < 0.02:
            agent.do_turn(0.0)
            return False
        kick_power = 0.0
        # kick_power = accel_radius / wm.self().kickRate()
        # kick_power = min(kick_power, i.maxPower())

        return agent.do_kick(kick_power,
                             accel_angle - wm.self().body())

# def calcAccel(self, agent, accel_radius: float, accel_angle: AngleDeg):
