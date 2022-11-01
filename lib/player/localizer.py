from lib.math.angle_deg import AngleDeg
from lib.math.vector_2d import Vector2D
from lib.rcsc.types import UNUM_UNKNOWN, LineID, MarkerID, SideID
from lib.rcsc.server_param import ServerParam
from lib.player.sensor.visual_sensor import VisualSensor


class Localizer:
    class PlayerT:
        def __init__(self) -> None:
            self.side_: SideID = SideID.NEUTRAL
            self.unum_: int = UNUM_UNKNOWN
            self.goalie_: bool = False
            self.pos_: Vector2D = Vector2D.invalid()
            self.rpos_: Vector2D = Vector2D.invalid()
            self.vel_: Vector2D = Vector2D.invalid()
            self.body_: float = 0
            self.face_: float = 0
            self.has_face_: bool = False
            self.arm_: float = 0
            self.pointto_: bool = False
            self.kicking_: bool = False
            self.tackle_: bool = False
        
        def reset(self):
            self.pos_.invalidate()
            self.rpos_.invalidate()
            self.unum_ = UNUM_UNKNOWN
            self.has_face_ = False
            self.pointto_ = False
            self.kicking_ = False
            self.tackle_ = False
        
        def has_vel(self):
            return self.vel_.is_valid()
        
        def has_angle(self):
            return self.has_face_
        
        def is_pointing(self):
            return self.pointto_
        
        def is_kicking(self):
            return self.kicking_
        
        def is_tackling(self):
            return self.tackle_
    
    def __init__(self) -> None:
        self._landmark_map: dict[MarkerID, Vector2D] = {}

        self._initial_landmark_map()
    
    def _initial_landmark_map(self):
        
        pitch_half_w = ServerParam.i().pitch_half_width()
        pitch_half_l = ServerParam.i().pitch_half_length()
        penalty_l = ServerParam.i().penalty_area_length()
        penalty_half_w = ServerParam.i().penalty_area_half_width()
        goal_half_w = ServerParam.i().goal_half_width()

        self._landmark_map[MarkerID.Goal_L] = Vector2D( -pitch_half_l, 0.0 )
        self._landmark_map[MarkerID.Goal_R] = Vector2D( +pitch_half_l, 0.0 )
        self._landmark_map[MarkerID.Flag_C] = Vector2D( 0.0, 0.0 )
        self._landmark_map[MarkerID.Flag_CT] = Vector2D( 0.0, -pitch_half_w )
        self._landmark_map[MarkerID.Flag_CB] = Vector2D( 0.0, +pitch_half_w )
        self._landmark_map[MarkerID.Flag_LT] = Vector2D( -pitch_half_l, -pitch_half_w )
        self._landmark_map[MarkerID.Flag_LB] = Vector2D( -pitch_half_l, +pitch_half_w )
        self._landmark_map[MarkerID.Flag_RT] = Vector2D( +pitch_half_l, -pitch_half_w )
        self._landmark_map[MarkerID.Flag_RB] = Vector2D( +pitch_half_l, +pitch_half_w )
        self._landmark_map[MarkerID.Flag_PLT] = Vector2D( -(pitch_half_l - penalty_l), -penalty_half_w )
        self._landmark_map[MarkerID.Flag_PLC] = Vector2D( -(pitch_half_l - penalty_l), 0.0 )
        self._landmark_map[MarkerID.Flag_PLB] = Vector2D( -(pitch_half_l - penalty_l), +penalty_half_w )
        self._landmark_map[MarkerID.Flag_PRT] = Vector2D( +(pitch_half_l - penalty_l), -penalty_half_w )
        self._landmark_map[MarkerID.Flag_PRC] = Vector2D( +(pitch_half_l - penalty_l), 0.0 )
        self._landmark_map[MarkerID.Flag_PRB] = Vector2D( +(pitch_half_l - penalty_l), +penalty_half_w )
        self._landmark_map[MarkerID.Flag_GLT] = Vector2D( -pitch_half_l, -goal_half_w )
        self._landmark_map[MarkerID.Flag_GLB] = Vector2D( -pitch_half_l, +goal_half_w )
        self._landmark_map[MarkerID.Flag_GRT] = Vector2D( +pitch_half_l, -goal_half_w )
        self._landmark_map[MarkerID.Flag_GRB] = Vector2D( +pitch_half_l, +goal_half_w )
        self._landmark_map[MarkerID.Flag_TL50] = Vector2D( -50.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_TL40] = Vector2D( -40.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_TL30] = Vector2D( -30.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_TL20] = Vector2D( -20.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_TL10] = Vector2D( -10.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_T0] = Vector2D( 0.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_TR10] = Vector2D( +10.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_TR20] = Vector2D( +20.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_TR30] = Vector2D( +30.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_TR40] = Vector2D( +40.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_TR50] = Vector2D( +50.0, -pitch_half_w - 5.0 )
        self._landmark_map[MarkerID.Flag_BL50] = Vector2D( -50.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_BL40] = Vector2D( -40.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_BL30] = Vector2D( -30.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_BL20] = Vector2D( -20.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_BL10] = Vector2D( -10.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_B0] = Vector2D( 0.0, pitch_half_w + 5.0)
        self._landmark_map[MarkerID.Flag_BR10] = Vector2D( +10.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_BR20] = Vector2D( +20.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_BR30] = Vector2D( +30.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_BR40] = Vector2D( +40.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_BR50] = Vector2D( +50.0, pitch_half_w + 5.0 )
        self._landmark_map[MarkerID.Flag_LT30] = Vector2D( -pitch_half_l - 5.0, -30.0 )
        self._landmark_map[MarkerID.Flag_LT20] = Vector2D( -pitch_half_l - 5.0, -20.0 )
        self._landmark_map[MarkerID.Flag_LT10] = Vector2D( -pitch_half_l - 5.0, -10.0 )
        self._landmark_map[MarkerID.Flag_L0] = Vector2D( -pitch_half_l - 5.0, 0.0 )
        self._landmark_map[MarkerID.Flag_LB10] = Vector2D( -pitch_half_l - 5.0, 10.0 )
        self._landmark_map[MarkerID.Flag_LB20] = Vector2D( -pitch_half_l - 5.0, 20.0 )
        self._landmark_map[MarkerID.Flag_LB30] = Vector2D( -pitch_half_l - 5.0, 30.0 )
        self._landmark_map[MarkerID.Flag_RT30] = Vector2D( +pitch_half_l + 5.0, -30.0 )
        self._landmark_map[MarkerID.Flag_RT20] = Vector2D( +pitch_half_l + 5.0, -20.0 )
        self._landmark_map[MarkerID.Flag_RT10] = Vector2D( +pitch_half_l + 5.0, -10.0 )
        self._landmark_map[MarkerID.Flag_R0] = Vector2D( +pitch_half_l + 5.0, 0.0 )
        self._landmark_map[MarkerID.Flag_RB10] = Vector2D( +pitch_half_l + 5.0, 10.0 )
        self._landmark_map[MarkerID.Flag_RB20] = Vector2D( +pitch_half_l + 5.0, 20.0 )
        self._landmark_map[MarkerID.Flag_RB30] = Vector2D( +pitch_half_l + 5.0, 30.0 )

    def get_face_dir_by_markers(self, markers: list[VisualSensor.MarkerT]):
        angle: float = None
        if len(markers) < 2:
            return angle
        
        marker1 = self._landmark_map.get(markers[0])
        if marker1 is None:
            return angle
        
        marker2 = self._landmark_map.get(markers[-1])
        if marker2 is None:
            return angle
        
        rpos1 = Vector2D.polar2vector(markers[0].dist_, markers[0].dir_)
        rpos2 = Vector2D.polar2vector(markers[-1].dist_, markers[-1].dir_)

        gap1 = rpos1 - rpos2
        gap2 = marker1 - marker2
        
        return (gap2.th() - gap1.th()).degree()
    
    def get_face_dir_by_line(self, lines: list[VisualSensor.LineT]):
        if len(lines) == 0:
            return None
        
        angle = lines[0].dir_
        angle += 90 if angle < 0 else -90

        l_id = lines[0].id_
        if l_id == LineID.Line_Left:
            angle = 180 - angle
        elif l_id == LineID.Line_Right:
            angle = -angle
        elif l_id == LineID.Line_Top:
            angle = -90 - angle
        elif l_id == LineID.Line_Bottom:
            angle = 90 - angle
        
        if len(lines) >= 2:
            angle += 180
        
        angle = AngleDeg.normalize_angle(angle)
        return angle
    
    def estimate_self_face(self, see: VisualSensor):
        face = self.get_face_dir_by_line()
        if face is None:
            face = self.get_face_dir_by_markers()
        
        return face                

    def localize_self(self, see:VisualSensor, self_face:float):
        markers = see.markers() + see.behind_markers()
        markers.sort(key=lambda x: x.dist_)
        
        if len(markers) == 0:
            return None
        
        pos: Vector2D = Vector2D(0,0)
        n_consider = min(5, len(markers))
        for marker in markers[:n_consider]:
            marker_pos = self._landmark_map[marker.id_]
            
            global_dir = marker.dir_ + self_face # TODO + BODY?
            estimated_pos = marker_pos - Vector2D(r=marker.dir_, theta=global_dir)
            
            pos += estimated_pos
        
        pos /= n_consider
        
        return pos

    def localize_ball_relative(self,
                               see: VisualSensor,
                               self_face: float) -> tuple[Vector2D, Vector2D]:
        if len(see.balls()) == 0:
            return None, None
        
        ball = see.balls()[0]
        rpos = Vector2D(r=ball.dist_, theta=ball.dir_)
        
        rvel = Vector2D.invalid()
        if ball.has_vel_:
            rvel = Vector2D(ball.dist_chng_, AngleDeg.deg2rad() * ball.dir_chng_ * ball.dist_)
            rvel.rotate(ball.dir_)
        
        return rpos, rvel

    def localize_player(self,
                        seen_player: VisualSensor.PlayerT,
                        self_face: float,
                        self_pos: Vector2D,
                        self_vel: Vector2D
                        ) -> PlayerT:
        player = Localizer.PlayerT()
        player.unum_ = seen_player.unum_
        player.goalie_ = seen_player.goalie_
        
        player.rpos_ = Vector2D(r=seen_player.dist_, theta=seen_player.dir_)
        player.pos_ = self_pos + player.rpos_
        
        if seen_player.has_vel_:
            player.vel_ = Vector2D(seen_player.dist_chng_,
                                   AngleDeg.deg2rad() * seen_player.dir_chng_ * seen_player.dist_)
            player.vel_.rotate(seen_player.dir_)
            player.vel_ += self_vel
        else:
            player.vel_.invalidate()
        
        player.has_face_ = False
        if (seen_player.body_  != VisualSensor.DIR_ERR
            and seen_player.face_ != VisualSensor.DIR_ERR):
            
            player.has_face_ = True
            player.body_ = AngleDeg.normalize_angle(seen_player.body_ + self_face)
            player.face_ = AngleDeg.normalize_angle(seen_player.face + self_face)
        
        player.pointto_ = False
        if seen_player.arm_ != VisualSensor.DIR_ERR:
            player.pointto_ = True
            player.arm_ = AngleDeg.normalize_angle(seen_player.arm_ + self_face)
        
        player.kicking_ = seen_player.kicking_
        player.tackle_ = seen_player.tackle_

        return player
    
            