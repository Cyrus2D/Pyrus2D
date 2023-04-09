from lib.action.hold_ball import HoldBall
from lib.action.neck_scan_players import NeckScanPlayers
from lib.action.smart_kick import SmartKick
from typing import List
from base.generator_action import KickAction, ShootAction, KickActionType
from base.generator_dribble import BhvDribbleGen
from base.generator_pass import BhvPassGen
from base.generator_shoot import BhvShhotGen
from base.generator_clear import BhvClearGen

from typing import TYPE_CHECKING

from lib.debug.debug import log
from lib.messenger.pass_messenger import PassMessenger

if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.player_agent import PlayerAgent


class BhvKick:
    def __init__(self):
        pass

    def execute(self, agent: 'PlayerAgent'):
        wm: 'WorldModel' = agent.world()
        shoot_candidate: ShootAction = BhvShhotGen().generator(wm)
        if shoot_candidate:
            log.debug_client().set_target(shoot_candidate.target_point)
            log.debug_client().add_message(
                'shoot' + 'to ' + shoot_candidate.target_point.__str__() + ' ' + str(shoot_candidate.first_ball_speed))
            SmartKick(shoot_candidate.target_point, shoot_candidate.first_ball_speed,
                      shoot_candidate.first_ball_speed - 1, 3).execute(agent)
            agent.set_neck_action(NeckScanPlayers())
            return True
        else:
            action_candidates: List[KickAction] = []
            action_candidates += BhvPassGen().generator(wm)
            action_candidates += BhvDribbleGen().generator(wm)

            if len(action_candidates) == 0:
                return self.no_candidate_action(agent)

            best_action: KickAction = max(action_candidates)

            target = best_action.target_ball_pos
            log.debug_client().set_target(target)
            log.debug_client().add_message(best_action.type.value + 'to ' + best_action.target_ball_pos.__str__() + ' ' + str(best_action.start_ball_speed))
            SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 1, 3).execute(agent)

            if best_action.type is KickActionType.Pass:
                agent.add_say_message(PassMessenger(best_action.target_unum,
                                                    best_action.target_ball_pos,
                                                    agent.effector().queued_next_ball_pos(),
                                                    agent.effector().queued_next_ball_vel()))

            agent.set_neck_action(NeckScanPlayers())
            return True

    def no_candidate_action(self, agent: 'PlayerAgent'):
        wm = agent.world()
        opp_min = wm.intercept_table().opponent_reach_cycle()
        if opp_min <= 3:
            action_candidates = BhvClearGen().generator(wm)
            if len(action_candidates) > 0:
                best_action: KickAction = max(action_candidates)
                target = best_action.target_ball_pos
                log.debug_client().set_target(target)
                log.debug_client().add_message(best_action.type.value + 'to ' + best_action.target_ball_pos.__str__() + ' ' + str(best_action.start_ball_speed))
                SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 2.0, 2).execute(agent)

        agent.set_neck_action(NeckScanPlayers())
        return HoldBall().execute(agent)