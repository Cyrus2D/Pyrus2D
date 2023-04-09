from pyrusgeom.rect_2d import Rect2D
from pyrusgeom.vector_2d import Vector2D

from base.generator_action import KickAction, KickActionType
from base.generator_pass import BhvPassGen
from lib.action.hold_ball import HoldBall
from lib.action.neck_scan_field import NeckScanField
from lib.action.neck_scan_players import NeckScanPlayers
from lib.action.smart_kick import SmartKick
from lib.debug.debug import log
from lib.messenger.pass_messenger import PassMessenger
from lib.rcsc.server_param import ServerParam

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class Bhv_GoalieSetPlay:
    _first_move: bool = False
    _second_move: bool = False
    _wait_count: int = 0

    def __init__(self):
        pass

    def execute(self, agent: 'PlayerAgent'):
        log.sw_log().team().add_text("Bhv_GoalieSetPlay execute")

        SP = ServerParam.i()
        wm = agent.world()
        gm = wm.game_mode()

        if not gm.type().is_goalie_catch_ball() or gm.side() != wm.our_side() or not wm.self().is_kickable():
            log.os_log().debug(f'### goalie set play gm.catch?={gm.type().is_goalie_catch_ball()}')
            log.os_log().debug(f'### goalie set play gm.side,ourside={gm.side()}, {wm.our_side()}')
            log.os_log().debug(f'### goalie set play iskick?={wm.self().is_kickable()}')
            log.sw_log().team().add_text('not a goalie catch mode')
            return False

        time_diff = wm.time().cycle() - agent.effector().catch_time().cycle()
        log.os_log().debug(f'### goalie set play catch_time={agent.effector().catch_time()}')
        log.os_log().debug(f'### goalie set play time diff={time_diff}')
        if time_diff <= 2:
            Bhv_GoalieSetPlay._first_move = False
            Bhv_GoalieSetPlay._second_move = False
            Bhv_GoalieSetPlay._wait_count = 0

            self.do_wait(agent)
            return True

        if not Bhv_GoalieSetPlay._first_move:
            move_point = Vector2D(SP.our_penalty_area_line_x() - 1.5, -13. if wm.ball().pos().y() < 0 else 13.)
            log.os_log().debug(f'### goalie set play move_point={move_point}')
            Bhv_GoalieSetPlay._first_move = True
            Bhv_GoalieSetPlay._second_move = False
            Bhv_GoalieSetPlay._wait_count = 0

            agent.do_move(move_point.x(), move_point.y())
            agent.set_neck_action(NeckScanField())
            return True

        our_penalty_area = Rect2D(Vector2D(-SP.pitch_half_length(), -40),
                                  Vector2D(-36, +40))
        if time_diff < 50. \
                or wm.set_play_count() < 3 \
                or (time_diff < SP.drop_ball_time() - 15
                    and (wm.self().stamina() < SP.stamina_max() * 0.9
                         or wm.exist_teammates_in(our_penalty_area, 20, True))):
            self.do_wait(agent)
            return True

        if not Bhv_GoalieSetPlay._second_move:
            move_point = self.get_kick_point(agent)
            log.os_log().debug(f'goalie set play move_point 2 ={move_point}')
            agent.do_move(move_point.x(), move_point.y())
            agent.set_neck_action(NeckScanField())
            Bhv_GoalieSetPlay._second_move = True
            Bhv_GoalieSetPlay._wait_count = 0
            return True

        Bhv_GoalieSetPlay._wait_count += 1

        if Bhv_GoalieSetPlay._wait_count < 5 or wm.see_time() != wm.time():
            self.do_wait(agent)
            return True

        Bhv_GoalieSetPlay._first_move = False
        Bhv_GoalieSetPlay._second_move = False
        Bhv_GoalieSetPlay._wait_count = 0

        self.do_kick(agent)

        return True

    def get_kick_point(self, agent: 'PlayerAgent'):
        base_x = -43.
        basy_y = 10.

        candids: list[tuple[Vector2D, float]] = []
        points = [
            Vector2D(base_x, basy_y),
            Vector2D(base_x, -basy_y),
            Vector2D(base_x, 0),
        ]

        for p in points:
            score = 0
            for o in agent.world().opponents_from_self():
                score += 1. / o.pos().dist2(p)
            candids.append((p, score))

        best_pos = candids[0][0]
        min_score = 100000
        for c in candids:
            if c[1] < min_score:
                min_score = c[1]
                best_pos = c[0]

        return best_pos

    def do_kick(self, agent: 'PlayerAgent'):
        wm = agent.world()
        action_candidates: list[KickAction] = []
        action_candidates += BhvPassGen().generator(wm)

        if len(action_candidates) == 0:
            agent.set_neck_action(NeckScanField())
            return HoldBall().execute(agent)

        best_action: KickAction = max(action_candidates)

        target = best_action.target_ball_pos
        log.debug_client().set_target(target)
        log.debug_client().add_message(
            best_action.type.value + 'to ' + best_action.target_ball_pos.__str__() + ' ' + str(
                best_action.start_ball_speed))
        SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 1, 3).execute(agent)

        if best_action.type is KickActionType.Pass:
            agent.add_say_message(PassMessenger(best_action.target_unum,
                                                best_action.target_ball_pos,
                                                agent.effector().queued_next_ball_pos(),
                                                agent.effector().queued_next_ball_vel()))

        agent.set_neck_action(NeckScanField())

    def do_wait(self, agent: 'PlayerAgent'):
        agent.set_neck_action(NeckScanField())
