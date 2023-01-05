from lib.player.player_agent import PlayerAgent
from lib.player.soccer_action import NeckAction
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType, ViewWidth
from lib.player.world_model import WorldModel

from pyrusgeom.geom_2d import AngleDeg, Rect2D, Size2D, Vector2D


class NeckScanField(NeckAction):
    INVALID_ANGLE = -360.
    
    _last_calc_time = GameTime(0, 0)
    _last_calc_view_width = ViewWidth.NORMAL
    _cached_target_angle = 0.0
    
    def __init__(self, NeckActions: list):
        super().__init__(NeckActions)
    
    def execute(self, agent: PlayerAgent):
        wm = agent.world()
        ef = agent.effector()
        
        if (NeckScanField._last_calc_time == wm.time()
            and NeckScanField._last_calc_view_width != ef.queued_next_view_width()): # TODO IMP FUNC
            
            agent.do_turn_neck(NeckScanField._cached_target_angle - ef.queued_next_self_body() - wm.self().neck()) # TODO IMP FUNC
            return True
        
        existed_ghost = False
        for p in wm.all_players():
            if p.is_ghost() and p.dist_from_self() < 30:
                existed_ghost = True
                break
        
        if not existed_ghost:
            angle = NeckScanPlayers.get_best_angle(agent) # TODO IMP FUNC
            if angle != NeckScanField.INVALID_ANGLE:
                NeckScanField._cached_target_angle = angle
                agent.do_turn_neck(NeckScanField._cached_target_angle - ef.queued_nest_self_body() - wm.self().neck())
                return True
        
        gt = wm.game_mode().type() 
        consider_patch = (
            gt is GameModeType.PlayOn
            or (
                not gt.is_ind_free_kick()
                and not gt.is_back_pass()
                and wm.ball().dist_from_self() < wm.self().player_type().player_size() + 0.15
            )
        )
        angle = self.calc_angle_default(agent, consider_patch) # TODO IMP FUNC
        
        if consider_patch and (AngleDeg(angle) - wm.self().face()).abs() < 5:
            angle = self.calc_angle_default(agent, False)
        
        NeckScanField._cached_target_angle = angle
        agent.do_turn_neck(NeckScanField._cached_target_angle - ef.queued_nest_self_body() - wm.self().neck())
        
        return True
    
    def calc_angle_default(self, agent: PlayerAgent, consider_patch: bool):
        SP = ServerParam.i()
        pitch_rect = Rect2D(
            Vector2D( -SP.pitch_half_length(), -SP.pitch_half_width()),
            Size2D(SP.pitch_length(), SP.pitch_width())
        )
        
        expand_pitch_rect = Rect2D(
            Vector2D( -SP.pitch_half_length() - 3, -SP.pitch_half_width()- 3),
            Size2D(SP.pitch_length()+6, SP.pitch_width()+6)
        )
        
        goalie_rect = Rect2D(
            Vector2D(SP.pitch_half_length() - 3, -15.),
            Size2D(10, 30)
        )
        
        wm = agent.world()
        ef = agent.effector()
        
        next_view_width = ef.queued_next_view_width().width()
        
        left_start = ef.queued_next_self_body() + SP.min_neck_angle() - (next_view_width*0.5) 
        scan_range = SP.max_neck_angle() - SP.min_neck_angle() + next_view_width
        shrinked_next_view_width = next_view_width - WorldModel.DIR_STEP * 1.5
        sol_angle = left_start + scan_range * 0.5
        if scan_range < shrinked_next_view_width:
            return sol_angle.degree()
        
        tmp_angle = left_start.copy()
        size_of_view_width = round(shrinked_next_view_width / WorldModel.DIR_STEP)
        dir_count:list[int] = []
        
        for _ in range(size_of_view_width):
            dir_count += wm.dir_count(tmp_angle)
            tmp_angle += WorldModel.DIR_STEP
        
        max_count_sum = 0
        add_dir = shrinked_next_view_width

        my_next = ef.queued_next_self_pos()

        while True:
            tmp_count_sum = sum(dir_count)
            angle = tmp_angle - shrinked_next_view_width *0.5
            
            if tmp_count_sum > max_count_sum:
                update = True
                if consider_patch:
                    face_point = my_next + Vector2D(r=20,a=angle)
                    if not pitch_rect.contains(face_point) and not goalie_rect.contains(face_point):
                        update = False
                    
                    if update:
                        left_face_point = my_next + Vector2D(r=20, a=angle - next_view_width * 0.5)
                        if not expand_pitch_rect.contains(left_face_point) and not goalie_rect.contains(left_face_point):
                            update = False
                    
                    if update:
                        right_face_point = my_next + Vector2D(r=20, a=angle + next_view_width * 0.5)
                        if not expand_pitch_rect.contains(right_face_point) and not goalie_rect.contains(right_face_point):
                            update = False
                    
                if update:
                    sol_angle = angle
                    max_count_sum = tmp_count_sum
            dir_count = dir_count[1:]
            add_dir += WorldModel.DIR_STEP
            tmp_angle += WorldModel.DIR_STEP
            dir_count.append(wm.dir_count(tmp_angle))
            
            if add_dir > scan_range:
                break
        return sol_angle.degree()