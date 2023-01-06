from math import exp
from lib.player.player_agent import PlayerAgent
from lib.player.soccer_action import NeckAction
from lib.rcsc.server_param import ServerParam
from lib.player.world_model import WorldModel

from pyrusgeom.soccer_math import bound
from pyrusgeom.geom_2d import Vector2D, AngleDeg

class NeckScanPlayers(NeckAction):
    INVALID_ANGLE = -360.0
    
    @staticmethod
    def get_best_angle(agent: PlayerAgent, min_neck_angle: float= INVALID_ANGLE, max_neck_angle:float = INVALID_ANGLE):
        wm = agent.world()
        
        if len(wm.all_players()) < 22:
            return NeckScanPlayers.INVALID_ANGLE    
        
        SP = ServerParam.i()
        ef = agent.effector()
        
        next_self_pos = ef.queued_next_self_pos()
        next_self_body = ef.queued_next_self_body()
        view_width = ef.queued_next_view_width().width()
        view_half_width = view_width/2
        
        neck_min = SP.min_neck_angle() if min_neck_angle == NeckScanPlayers.INVALID_ANGLE else bound(SP.min_neck_angle(), min_neck_angle, SP.max_neck_angle())
        neck_max = SP.max_neck_angle() if max_neck_angle == NeckScanPlayers.INVALID_ANGLE else bound(SP.min_neck_angle(), max_neck_angle, SP.max_neck_angle())
        neck_step = max(1, (neck_max - neck_min)/36)
        
        best_dir = NeckScanPlayers.INVALID_ANGLE
        best_score = 0.
        
        dirs = [neck_min + d*neck_step for d in range(36)]
        for dir in dirs:
            left_angle = next_self_body+(dir - (view_half_width - 0.01))
            right_angle = next_self_body + (dir + (view_half_width - 0.01))
            
            score = NeckScanPlayers.calculate_score(wm, next_self_pos, left_angle, right_angle) # TODO IMP FUNC
            if score > best_score:
                best_dir = dir
                best_score = score
        
        if best_dir == NeckScanPlayers.INVALID_ANGLE or abs(best_score) < 1.0e-5:
            return NeckScanPlayers.INVALID_ANGLE
        
        angle = next_self_body + best_dir
        return angle.degree()
    
    @staticmethod
    def calculate_score(wm: WorldModel, next_self_pos: Vector2D, left_angle: AngleDeg, right_angle: AngleDeg):
        score = 0.
        view_buffer = 90.

        it = wm.intercept_table()
        our_min = min(it.self_reach_cycle(), it.teammate_reach_cycle())
        opp_min = it.opponent_reach_cycle()

        our_ball = (our_min <= opp_min)

        reduced_left_angle = left_angle + 5.
        reduced_right_angle = right_angle - 5.
        
        for p in wm.all_players():
            if p.is_self():
                continue
            
            pos = p.pos() + p.vel()
            angle = (pos - next_self_pos).th()
            
            if not angle.is_right_of(reduced_left_angle) or not angle.is_left_of(reduced_right_angle):
                continue
            
            if p.ghost_count() >= 5:
                continue
            
            pos_count= p.seen_pos_count()
            if p.is_ghost() and p.ghost_count() % 2 == 1:
                pos_count = min(2, pos_count)
            
            pos_count += 1
            
            if our_ball:
                if p.side() == wm.our_side() and (p.pos().x() > wm.ball().pos().x - 10 or p.pos().x() > 30):
                    pos_count *=2
            
            base_val = pos_count**2
            rate = exp(-(p.dist_from_self() ** 2) / (2*(20**2)))

            score += base_val * rate
            buf = min((angle-left_angle).abs(), (angle-right_angle).abs())
            
            if buf < view_buffer:
                view_buffer = buf
        
        rate = 1+ view_buffer/90
        score*= rate
        return score

        
        