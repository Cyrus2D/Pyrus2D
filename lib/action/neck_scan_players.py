from math import exp
from lib.action.neck_scan_field import NeckScanField
from lib.debug.debug import log
from lib.debug.level import Level
from lib.player.soccer_action import NeckAction
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.player.world_model import WorldModel

from pyrusgeom.soccer_math import bound
from pyrusgeom.geom_2d import Vector2D, AngleDeg

from typing import TYPE_CHECKING

from lib.rcsc.types import ViewWidth
if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent

class NeckScanPlayers(NeckAction):
    DEBUG = True
    
    INVALID_ANGLE = -360.0
    
    _last_calc_time = GameTime(0, 0)
    _last_calc_view_width = ViewWidth.NORMAL
    _cached_target_angle = 0.0
    _last_calc_min_neck_angle = 0.
    _last_calc_max_neck_angle = 0.
    
    def __init__(self, min_neck_angle: float=INVALID_ANGLE, max_neck_angle: float= INVALID_ANGLE):
        super().__init__()
        
        self._min_neck_angle = min_neck_angle
        self._max_neck_angle = max_neck_angle
        
    def execute(self, agent: 'PlayerAgent'):
        log.debug_client().add_message('ScanPlayers/')
        wm = agent.world()
        ef = agent.effector()
        
        if NeckScanPlayers.DEBUG:
            log.sw_log().world().add_text( f"(NSP exe) last={NeckScanPlayers._last_calc_time}|wm-time={wm.time()}")

        if (NeckScanPlayers._last_calc_time != wm.time()
            or NeckScanPlayers._last_calc_view_width != ef.queued_next_view_width()
            or abs(NeckScanPlayers._last_calc_min_neck_angle - self._min_neck_angle) > 1.0e-3
            or abs(NeckScanPlayers._last_calc_max_neck_angle - self._max_neck_angle) > 1.0e-3):
            
            NeckScanPlayers._last_calc_time = wm.time().copy()
            NeckScanPlayers._last_calc_view_width = ef.queued_next_view_width()
            NeckScanPlayers._last_calc_min_neck_angle = self._min_neck_angle
            NeckScanPlayers._last_calc_max_neck_angle = self._max_neck_angle
            
            NeckScanPlayers._cached_target_angle = NeckScanPlayers.get_best_angle(agent, self._min_neck_angle, self._max_neck_angle)
        
        if NeckScanPlayers._cached_target_angle == NeckScanPlayers.INVALID_ANGLE:
            return NeckScanField().execute(agent)
        
        target_angle = AngleDeg(NeckScanPlayers._cached_target_angle)
        agent.do_turn_neck(target_angle - ef.queued_next_self_body().degree() - wm.self().neck().degree())
        return True
    
    @staticmethod
    def get_best_angle(agent: 'PlayerAgent', min_neck_angle: float= INVALID_ANGLE, max_neck_angle:float = INVALID_ANGLE):
        wm = agent.world()
        
        if len(wm.all_players()) < 22:
            if NeckScanPlayers.DEBUG:
                log.sw_log().world().add_text( f"(NSP GBA) all players are less than 22, n={len(wm.all_players())}")
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

            if NeckScanPlayers.DEBUG:
                log.sw_log().world().add_text( f"body={next_self_body}|dir={dir}|score={score}")    
                
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
                if p.side() == wm.our_side() and (p.pos().x() > wm.ball().pos().x() - 10 or p.pos().x() > 30):
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

        
        