"""
  \ file body_stop_ball.py
  \ brief kick the ball to keep a current positional relation.
"""

from lib.player.soccer_action import *
from pyrusgeom.soccer_math import *
from pyrusgeom.angle_deg import AngleDeg
from lib.rcsc.server_param import ServerParam

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.player_agent import PlayerAgent
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
        self._accel_radius = 0.0
        self._accel_angle = AngleDeg()

    """
      \ brief execute action
      \ param agent the agent itself
      \ return True if action is performed
    """

    def execute(self, agent: 'PlayerAgent'):
        wm: 'WorldModel' = agent.world()
        if not wm.self().is_kickable():
            return False
        if not wm.ball().vel_valid():  # Always true until NFS nice :)
            required_accel = wm.self().vel() - (wm.self().pos() - wm.ball().pos())
            kick_power = required_accel.r() / wm.self().kick_rate()
            kick_power *= 0.5
            agent.do_kick(min(kick_power, ServerParam.i().max_power()),
                          required_accel.th() - wm.self().body())
            return True

        self._accel_radius = 0.0
        self._accel_angle = AngleDeg()

        self.calcAccel(agent)

        if self._accel_radius < 0.02:
            agent.do_turn(0.0)
            return False
        kick_power = 0.0
        # kick_power = self._accel_radius / wm.self().kickRate()
        # kick_power = min(kick_power, i.maxPower())

        return agent.do_kick(kick_power,
                             self._accel_angle - wm.self().body())

    def calcAccel(self, agent):

        wm: 'WorldModel' = agent.world()

        safety_dist = wm.self().player_type().player_size() + ServerParam.i().ball_size() + 0.1

        target_dist = wm.ball().dist_from_self()
        if target_dist < safety_dist:
            target_dist = safety_dist

        if target_dist > wm.self().player_type().kickable_area() - 0.1:
            target_dist = wm.self().player_type().kickable_area() - 0.1

        target_rel = wm.self().pos() - wm.ball().pos()
        target_rel.set_length(target_dist)

        required_accel = wm.self().vel()
        required_accel += target_rel  # target relative to current
        required_accel -= wm.self().pos() - wm.ball().pos()  # vel = pos diff
        required_accel -= wm.ball().vel()  # required accel

        self._accel_radius = required_accel.r()

        if self._accel_radius < 0.01:
            return None

            # check max accel with player's kick rate

        max_accel = ServerParam.i().max_power() * wm.self().kick_rate()
        if max_accel > self._accel_radius:
            # can accelerate -. can stop ball successfully
            self._accel_angle = required_accel.th()
            return None

        ##################################
        # keep the ball as much as possible near the best point

        next_ball_to_self = wm.self().vel()
        next_ball_to_self -= wm.self().pos() - wm.ball().pos()
        next_ball_to_self -= wm.ball().vel()

        keep_dist = wm.self().player_type().player_size() + wm.self().player_type().kickable_margin() * 0.4

        self._accel_radius = min(max_accel, next_ball_to_self.r() - keep_dist)
        self._accel_angle = next_ball_to_self.th()

        if self._accel_radius < 0.0:  # == next_ball_dist < keep_dist
            # next ball dist will be closer than keep dist.
            #  -. kick angle must be reversed.
            self._accel_radius *= -1.0
            self._accel_radius = min(self._accel_radius, max_accel)
            self._accel_angle -= 180.0
