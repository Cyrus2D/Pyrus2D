
from typing import TYPE_CHECKING

from pyrusgeom.line_2d import Line2D
from pyrusgeom.rect_2d import Rect2D
from pyrusgeom.size_2d import Size2D
from pyrusgeom.vector_2d import Vector2D

from base.generator_action import KickAction
from base.generator_pass import BhvPassGen
from lib.action.go_to_point import GoToPoint
from lib.action.hold_ball import HoldBall
from lib.action.intercept import Intercept
from lib.action.neck_scan_players import NeckScanPlayers
from lib.action.neck_turn_to_ball import NeckTurnToBall
from lib.action.smart_kick import SmartKick
from lib.debug.color import Color
from lib.debug.debug_print import debug_print
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.rcsc.server_param import ServerParam

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


DEBUG = True

def decision(agent: 'PlayerAgent'):
    SP = ServerParam.i()
    wm = agent.world()

    our_penalty = Rect2D(Vector2D(-SP.pitch_half_length(), -SP.penalty_area_half_width() + 1),
                         Size2D(SP.penalty_area_length() - 1, SP.penalty_area_width() - 2))

    if (wm.time().cycle() > wm.self().catch_time().cycle() + SP.catch_ban_cycle()
        and wm.ball().dist_from_self() < SP.catchable_area() - 0.05
        and our_penalty.contains(wm.ball().pos())):

        agent.do_catch()
        agent.set_neck_action(NeckTurnToBall())
    elif wm.self().is_kickable():
        do_kick(agent)
    else:
        do_move(agent)

    return True

def do_kick(agent: 'PlayerAgent'):
    wm = agent.world()

    action_candidates = BhvPassGen().generator(wm)

    if len(action_candidates) == 0:
        agent.set_neck_action(NeckScanPlayers())
        return HoldBall().execute(agent)

    best_action: KickAction = max(action_candidates)
    target = best_action.target_ball_pos
    debug_print(best_action)
    agent.debug_client().set_target(target)
    agent.debug_client().add_message(best_action.type.value + 'to ' + best_action.target_ball_pos.__str__() + ' ' + str(
        best_action.start_ball_speed))
    SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 1, 3).execute(agent)
    agent.set_neck_action(NeckScanPlayers())
    return True


def do_move(agent: 'PlayerAgent'):
    SP = ServerParam.i()
    wm = agent.world()

    # if Tackle(0.8, 90.).execute(agent): # TODO IMP FUNC
    #     return True

    self_min = wm.intercept_table().self_reach_cycle()
    tm_min = wm.intercept_table().teammate_reach_cycle()
    opp_min = wm.intercept_table().opponent_reach_cycle()

    if self_min < tm_min and self_min < opp_min - 10:
        Intercept(False).execute(agent)
        agent.set_neck_action(NeckTurnToBall())
        return True

    ball_pos = wm.ball().inertia_point(min(tm_min, opp_min))

    post1 = Vector2D(-SP.pitch_half_length(), +SP.goal_half_width())
    post2 = Vector2D(-SP.pitch_half_length(), -SP.goal_half_width())

    ball_to_post1 = (post1 - ball_pos).th()
    ball_to_post2 = (post2 - ball_pos).th()
    ball_dir = (ball_to_post1 + ball_to_post2).degree()/ 2

    ball_move_line = Line2D(ball_pos, ball_dir)

    margin = min(-SP.pitch_half_length() + 3, ball_pos.x() - 0.1)
    goalie_move_line = Line2D(Vector2D(margin, -SP.pitch_half_width()),
                              Vector2D(margin, +SP.pitch_half_width()))

    target = goalie_move_line.intersection(ball_move_line)

    if DEBUG:
        dlog.add_line(Level.POSITIONING,
                      start=Vector2D(ball_pos.x(), ball_move_line.get_y(ball_pos.x())),
                      end=Vector2D(-SP.pitch_half_length(), ball_move_line.get_y(-SP.pitch_half_length())),
                      color=Color(string='red'))
        dlog.add_line(Level.POSITIONING,
                      start=Vector2D(goalie_move_line.get_x(-30), -30),
                      end=Vector2D(goalie_move_line.get_x(+30), +30),
                      color=Color(string='red'))

    if target:
        GoToPoint(target, 0.2, 100).execute(agent)
        agent.set_neck_action(NeckTurnToBall())
        return True

    return False










