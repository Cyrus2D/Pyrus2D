from lib.player.templates import *
from lib.action.smart_kick import SmartKick
from typing import List
from base.generator_action import KickAction
from base.generator_dribble import BhvDribbleGen
from base.generator_pass import BhvPassGen


class BhvKick:
    def __init__(self):
        pass

    def execute(self, agent):
        wm: WorldModel = agent.world()
        action_candidates: List[KickAction] = []
        action_candidates += BhvPassGen().generator(wm)
        action_candidates += BhvDribbleGen().generator(wm)
        if len(action_candidates) is 0:
            return True

        best_action: KickAction = max(action_candidates)

        target = best_action.target_ball_pos
        print(best_action)
        agent.debug_client().set_target(target)
        agent.debug_client().add_message(best_action.type.value + 'to ' + best_action.target_ball_pos.__str__() + ' ' + str(best_action.start_ball_speed))
        SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 1, 3).execute(agent)

