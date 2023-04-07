from typing import TYPE_CHECKING

from pyrusgeom.line_2d import Line2D
from pyrusgeom.ray_2d import Ray2D
from pyrusgeom.vector_2d import Vector2D

from base.tackle_generator import TackleGenerator
from lib.action.neck_turn_to_point import NeckTurnToPoint
from lib.debug.debug import log
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import Card

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class BasicTackle:
    def __init__(self, min_prob: float, body_thr: float):
        self._min_prob: float = min_prob
        self._body_thr: float = body_thr

    def execute(self, agent: 'PlayerAgent'):
        SP = ServerParam.i()
        wm = agent.world()

        use_foul = False
        tackle_prob = wm.self().tackle_probability()

        if wm.self().card() == Card.NO_CARD \
                and (wm.ball().pos().x() > SP.our_penalty_area_line_x() + 0.5
                     or wm.ball().pos().abs_y() > SP.penalty_area_half_width() + 0.5) \
                and tackle_prob < wm.self().foul_probability():
            tackle_prob = wm.self().foul_probability()
            use_foul = True

        if tackle_prob < self._min_prob:
            return False

        self_min = wm.intercept_table().self_reach_cycle()
        mate_min = wm.intercept_table().teammate_reach_cycle()
        opp_min = wm.intercept_table().opponent_reach_cycle()

        self_reach_point = wm.ball().inertia_point(self_min)

        self_goal = False
        if self_reach_point.x() < - SP.pitch_half_length():
            ball_ray = Ray2D(wm.ball().pos(), wm.ball().vel().th())
            goal_line = Line2D(Vector2D(-SP.pitch_half_length(), +10),
                               Vector2D(-SP.pitch_half_length(), -10))

            intersect = ball_ray.intersection(goal_line)
            if intersect and intersect.is_valid() \
                    and intersect.abs_y() < SP.goal_half_width() + 1.:
                self_goal = True

        if not (wm.kickable_opponent()
                or self_goal
                or (opp_min < self_min - 3 and opp_min < mate_min - 3)
                or (self_min >= 5
                    and wm.ball().pos().dist2(SP.their_team_goal_pos()) < 10 **2
                    and ((SP.their_team_goal_pos() - wm.self().pos()).th() - wm.self().body()).abs() < 45.)):

            return False

        return self.executeV14(agent, use_foul)

    def executeV14(self, agent: 'PlayerAgent', use_foul: bool):
        wm = agent.world()

        result = TackleGenerator.instance().best_result(wm)

        ball_next = wm.ball().pos() + result._ball_vel

        log.debug_client().add_message(f"Basic{'Foul' if use_foul else 'Tackle'}{result._tackle_angle.degree()}")
        tackle_dir = (result._tackle_angle - wm.self().body()).degree()

        agent.do_tackle(tackle_dir, use_foul)
        agent.set_neck_action(NeckTurnToPoint(ball_next))
        return True
































