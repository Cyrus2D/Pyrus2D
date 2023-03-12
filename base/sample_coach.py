import functools
from lib.coach.coach_agent import CoachAgent
from lib.debug.debug import log
from lib.rcsc.player_type import PlayerType
from lib.rcsc.types import HETERO_DEFAULT, HETERO_UNKNOWN

import team_config

def real_speed_max(lhs: PlayerType, rhs: PlayerType) -> bool:
    if abs(lhs.real_speed_max() - rhs.real_speed_max()) < 0.005:
        return lhs.cycles_to_reach_max_speed() < rhs.cycles_to_reach_max_speed()
    return lhs.real_speed_max() > rhs.real_speed_max() 

class SampleCoach(CoachAgent):
    def __init__(self):
        super().__init__()
        
        self._first_sub = False
        
    def action_impl(self):
        # TODO Send Team Graphic
        
        self.do_substitute()
    
    def do_substitute(self):
        if (not self._first_sub
            and self.world().time().cycle() == 0
            and self.world().time().stopped_cycle() > 10):
            
            self.do_first_subsititute()
            self._first_sub = True
            return
    
    def do_first_subsititute(self):
        candidates: list[PlayerType] = []
        
        for i, pt in enumerate(self.world().player_types()):
            if pt is None:
                log.os_log().error(f"(sample coach first sub) pt is None! index={i}")
                continue
            
            for i in range(1): # TODO PLAYER PARAM
                candidates.append(pt)
        
        unum_order = [11,2,3,10,9,6,4,5,7,8]
        
        self.subsititute_to(1, HETERO_DEFAULT)
        for pt in candidates:
            if pt.id() == HETERO_DEFAULT:
                candidates.remove(pt)
                break
        
        for unum in unum_order:
            p = self.world().our_player(unum)
            if p is None:
                log.os_log().error(f"(sample coach sub to) player is None! unum={unum}")
                continue
            type = self.get_fastest_type(candidates)
            if type != HETERO_UNKNOWN:
                self.subsititute_to(unum, type)
        
    def subsititute_to(self, unum, type):
        if self.world().time().cycle() > 0 and self.world().our_subsititute_count() >= 3: # TODO PLAYER PARAM
            log.os_log().error(f"(sample coach subsititute to) WARNING: {team_config.TEAM_NAME} coach: over the substitution max."
                  f"cannot change player({unum}) to {type}")
            return
        
        if type not in self.world().available_player_type_id(): # IMP FUNC
            log.os_log().error(f"(sample coach subsititute to) type is not available. type={type}")
            return
        
        self.do_change_player_type(unum, type)
        log.os_log().error(f"(sample coach subsititute to) player({unum})'s type changed to {type}")
    
    def get_fastest_type(self, candidates: list[PlayerType]):
        if len(candidates) == 0:
            return HETERO_UNKNOWN
        
        candidates.sort(key=functools.cmp_to_key(real_speed_max))
        
        best_type: PlayerType = None
        max_speed = 0
        min_cycle = 100
        
        for candidate in candidates:
            if candidate.real_speed_max() < max_speed - 0.01:
                break
            
            if candidate.cycles_to_reach_max_speed() < min_cycle:
                best_type = candidate
                max_speed = best_type.real_speed_max()
                min_cycle = best_type.cycles_to_reach_max_speed()
                continue
            
            if candidate.cycles_to_reach_max_speed() == min_cycle:
                if candidate.get_one_step_stamina_consumption() < best_type.get_one_step_stamina_consumption():
                    best_type = candidate
                    max_speed = best_type.real_speed_max()
        
        if best_type is not None:
            id = best_type.id()
            candidates.remove(best_type)
            return id
        return HETERO_UNKNOWN