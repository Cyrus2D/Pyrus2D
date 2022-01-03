from lib.player.templates import *
from lib.action.smart_kick import SmartKick
from typing import List
from base.generator_action import KickAction, ShootAction
from base.generator_dribble import BhvDribbleGen
from base.generator_pass import BhvPassGen
from base.generator_shoot import BhvShhotGen


class BhvKick:
    def __init__(self):
        pass

    def execute(self, agent):
        wm: WorldModel = agent.world()
        shoot_candidate: ShootAction = BhvShhotGen().generator(wm)
        if shoot_candidate:
            agent.debug_client().set_target(shoot_candidate.target_point)
            agent.debug_client().add_message(
                'shoot' + 'to ' + shoot_candidate.target_point.__str__() + ' ' + str(shoot_candidate.first_ball_speed))
            SmartKick(shoot_candidate.target_point, shoot_candidate.first_ball_speed,
                      shoot_candidate.first_ball_speed - 1, 3).execute(agent)
            return True
        else:
            action_candidates: List[KickAction] = []
            action_candidates += BhvPassGen().generator(wm)
            action_candidates += BhvDribbleGen().generator(wm)
            if len(action_candidates) == 0:
                return True

            best_action: KickAction = max(action_candidates)

            target = best_action.target_ball_pos
            print(best_action)
            agent.debug_client().set_target(target)
            agent.debug_client().add_message(best_action.type.value + 'to ' + best_action.target_ball_pos.__str__() + ' ' + str(best_action.start_ball_speed))
            SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 1, 3).execute(agent)
            return True
