from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.math_values import DEG2RAD
from pyrusgeom.vector_2d import Vector2D
from pyrusgeom.sector_2d import Sector2D
from lib.player.object_table import ObjectTable, DataEntry
from lib.debug.debug_print import debug_print
from lib.rcsc.types import UNUM_UNKNOWN, LineID, MarkerID, SideID
from lib.rcsc.server_param import ServerParam
from lib.player.sensor.visual_sensor import VisualSensor
from lib.debug.logger import dlog
from lib.debug.level import Level
from lib.debug.color import Color
from lib.rcsc.types import ViewWidth
from pyrusgeom.soccer_math import min_max
import math


class Localizer:
    DEBUG = True
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
        self._object_table = ObjectTable()
        self._landmark_map: dict[MarkerID, Vector2D] = {}
        self._points = []

    def get_face_dir_by_markers(self, markers: list[VisualSensor.MarkerT], view_width: ViewWidth):
        if len(markers) < 2:
            return None
        
        marker1 = self._object_table.landmark_map.get(markers[0])
        if marker1 is None:
            return None
        
        marker2 = self._object_table.landmark_map.get(markers[-1])
        if marker2 is None:
            return None
        marker1_dist_avg, marker1_dist_err = self._object_table.get_landmark_distance_range(view_width, markers[0].dist_)
        marker2_dist_avg, marker2_dist_err = self._object_table.get_landmark_distance_range(view_width, markers[-1].dist_)
        rpos1 = Vector2D.polar2vector(marker1_dist_avg, markers[0].dir_)
        rpos2 = Vector2D.polar2vector(marker2_dist_avg, markers[-1].dir_)

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
    
    def estimate_self_face(self, see: VisualSensor, view_width: ViewWidth):
        face = self.get_face_dir_by_line(see.lines())
        if face is None:
            face = self.get_face_dir_by_markers(see.markers(), view_width)
        
        if Localizer.DEBUG:
            dlog.add_text(Level.WORLD, f"(estimate self face) face={face}")
        
        return face                

    def localize_self(self, see:VisualSensor, self_face:float):
        if Localizer.DEBUG:
            dlog.add_text(Level.WORLD, f"(localize self) started {'#'*20}")
            

        markers = see.markers() + see.behind_markers()
        markers.sort(key=lambda x: x.dist_)
        
        if len(markers) == 0:
            return None
        
        pos: Vector2D = Vector2D(0,0)
        n_consider = 0
        for marker in markers:
            if n_consider >= 5:
                continue
            if marker.id_ is VisualSensor.ObjectType.Obj_Unknown:
                continue
            marker_pos = self._object_table.landmark_map[marker.id_]

            if Localizer.DEBUG:
                dlog.add_text(Level.WORLD, f"(localize self) considered-marker[{marker.id_}]={marker_pos}")
                dlog.add_circle(Level.WORLD, center=marker_pos, r=0.25, fill=True, color=Color(string="black"))

            
            global_dir = marker.dir_ + self_face
            estimated_pos = marker_pos - Vector2D(r=marker.dist_, a=global_dir)
            
            if Localizer.DEBUG:
                dlog.add_text(Level.WORLD, f"(localize self) estimated-pos={estimated_pos}")
                dlog.add_circle(Level.WORLD, center=estimated_pos, r=0.25, fill=True, color=Color(string="red"))
            
            pos += estimated_pos
            n_consider += 1

        debug_print(f"lls n_c={n_consider}")
        if n_consider == 0:
            return None
        pos /= n_consider

        if Localizer.DEBUG:
            dlog.add_text(Level.WORLD, f"(localize self) pos={pos}")
            dlog.add_circle(Level.WORLD, center=pos, r=0.25, fill=True, color=Color(string="blue"))
        
        return pos

    def get_dir_range(self, seen_dir, self_face, self_face_error):
        return seen_dir + self_face, 0.5 + self_face_error

    def generate_points(self, view_width: ViewWidth, marker, marker_id: MarkerID, self_face: float, self_face_error: float):
        marker_pos = self._object_table.landmark_map.get(marker_id)
        if marker_pos is None:
            return
        ave_dist, dist_err = self._object_table.get_landmark_distance_range(view_width, marker.dist_)
        ave_dir, dir_err = self.get_dir_range(marker.dir_, self_face, self_face_error)
        ave_dir += 180.0
        min_dist = ave_dist - dist_err
        dist_range = dist_err * 2.0
        dist_inc = max(0.01, dist_err / 16.0)
        dist_loop = min_max(2, int(math.ceil(dist_range / dist_inc)), 16)
        dist_inc = dist_range / (dist_loop - 1)
        dir_range = dir_err * 2.0
        circum = 2.0 * ave_dist * 3.141592 * (dir_range / 360.0)
        circum_inc = max(0.01, circum / 32.0)
        dir_loop = int(min_max(2, int(math.ceil(circum / circum_inc)), 32))
        dir_inc = dir_range / (dir_loop - 1)
        base_angle = AngleDeg(ave_dir - dir_err)
        for i_dir in range(dir_loop):
            base_angle += dir_inc
            base_vec = Vector2D.polar2vector(1.0, base_angle)
            add_dist = 0.0
            for i_dist in range(dir_loop):
                add_dist += dist_inc
                self._points.append(marker_pos + (base_vec * (min_dist + add_dist)))

    def update_points_by_markers(self, view_width: ViewWidth, markers, self_face: float, self_face_error: float):
        counter = 0
        for i in range(1, len(markers)):
            if counter >= 30:
                break
            self.update_points_by(view_width, markers[i], markers[i].id_, self_face, self_face_error)
            self.resample_points(view_width, markers[0], markers[0].id_, self_face, self_face_error)

    def update_points_by(self, view_width: ViewWidth, marker, marker_id, self_face: float, self_face_error: float):
        marker_pos = self._object_table.landmark_map.get(marker_id)
        ave_dist, dist_error = self._object_table.get_landmark_distance_range(view_width, marker.dist_)

        ave_dir, dir_error = self.get_dir_range(marker.dir_, self_face, self_face_error)
        ave_dir += 180.0

        sector = Sector2D(marker_pos, ave_dist - dist_error, ave_dist + dist_error, AngleDeg(ave_dir - dir_error), AngleDeg(ave_dir + dir_error))
        self._points = list(filter(lambda p: sector.contains(p), self._points))

    def resample_points(self, view_width: ViewWidth, marker, marker_id, self_face: float, self_face_error: float):
        if len(self._points) >= 50:
            return
        if len(self._points) == 0:
            self.generate_points(view_width, marker, marker_id, self_face, self_face_error)
            return
        import random
        point_size = len(self._points)
        for i in range(len(self._points), 51):
            choose_index = random.randint(0, point_size - 1)
            self._points.append(self._points[choose_index] + Vector2D(random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01)))

    def average_points(self):
        ave_pos = Vector2D(0.0, 0.0)
        ave_err = Vector2D(0.0, 0.0)
        if len(self._points) == 0:
            return None, Vector2D(0, 0)
        max_x = self._points[0].x()
        min_x = max_x
        max_y = self._points[0].y()
        min_y = max_y
        for p in self._points:
            ave_pos += p
            if p.x() > max_x:
                max_x = p.x()
            elif p.x() < min_x:
                min_x = p.x()
            if p.y() > max_y:
                max_y = p.y()
            elif p.y() < min_y:
                min_y = p.y()
        ave_pos = ave_pos / float(len(self._points))
        ave_err.set_x((max_x - min_x) / 2.0)
        ave_err.set_y((max_y - min_y) / 2.0)
        return ave_pos, ave_err

    def get_nearest_marker(self, object_type: VisualSensor.ObjectType, pos: Vector2D):
        if object_type == VisualSensor.ObjectType.Obj_Goal_Behind:
            return MarkerID.Goal_L if pos.x() < 0.0 else MarkerID.Goal_R
        min_dist2 = 3.0 * 3.0
        candidate = MarkerID.Marker_Unknown
        for m, p in self._object_table.landmark_map.items():
            d2 = pos.dist(p)
            if d2 < min_dist2:
                min_dist2 = d2
                candidate = m
        return candidate

    def update_points_by_behind_marker(self, view_width, markers, behind_markers, self_pos, self_face, self_face_error):
        if len(behind_markers) == 0:
            return
        marker_id = self.get_nearest_marker(behind_markers[0].object_type_, self_pos)
        if marker_id == MarkerID.Marker_Unknown:
            return
        self.update_points_by(view_width, behind_markers[0], marker_id, self_face, self_face_error)
        if len(self._points) == 0:
            return

        self.generate_points(view_width, behind_markers[0], marker_id, self_face, self_face_error)
        if len(self._points) == 0:
            return

        counter = 0
        for i in range(1, len(markers)):
            if counter >= 20:
                break
            self.update_points_by(view_width, markers[i], markers[i].id_, self_face, self_face_error)
            self.resample_points(view_width, markers[0], markers[0].id_, self_face, self_face_error)

    def localize_self2(self, see: VisualSensor, view_width: ViewWidth, self_face: float, self_face_error: float):
        if len(see.markers()) == 0:
            return None, Vector2D(0, 0)
        self._points.clear()
        markers = see.markers() + see.behind_markers()
        markers.sort(key=lambda x: x.dist_)

        self.generate_points(view_width, markers[0], markers[0].id_, self_face, self_face_error)
        if len(self._points) == 0:
            return None, Vector2D(0, 0)
        self.update_points_by_markers(view_width, markers, self_face, self_face_error)
        self_pos, self_pos_err = self.average_points()

        if len(see.behind_markers()) == 0:
            return self_pos, self_pos_err
        self.update_points_by_behind_marker(view_width, see.markers(), see.behind_markers(), self_pos, self_face, self_face_error)
        self_pos, self_pos_err = self.average_points()
        return self_pos, self_pos_err

    def localize_ball_relative(self,
                               see: VisualSensor,
                               self_face: float) -> tuple[Vector2D, Vector2D]:
        self_face = float(self_face)
        if Localizer.DEBUG:
            dlog.add_text(Level.WORLD, f"(localize ball relative) started {'#'*20}")

        if len(see.balls()) == 0:
            return None, None
        
        ball = see.balls()[0]
        global_dir = float(ball.dir_) + self_face

        rpos = Vector2D(r=ball.dist_, a=global_dir)

        if Localizer.DEBUG:
            dlog.add_text(Level.WORLD, f"(localize ball relative) ball: r={ball.dist_}, t={ball.dir_}")
            dlog.add_text(Level.WORLD, f"(localize ball relative) rpos={rpos}")

        
        rvel = Vector2D.invalid()
        if ball.has_vel_:
            rvel = Vector2D(ball.dist_chng_, DEG2RAD * ball.dir_chng_ * ball.dist_)
            rvel.rotate(global_dir)
            if Localizer.DEBUG:
                dlog.add_text(Level.WORLD, f"(localize ball relative) has_vel")
                dlog.add_text(Level.WORLD, f"(localize ball relative) vel={rvel}")
                dlog.add_text(Level.WORLD, f"(localize ball relative) ball={ball}")
        
        return rpos, rvel

    def localize_player(self,
                        seen_player: VisualSensor.PlayerT,
                        self_face: float,
                        self_pos: Vector2D,
                        self_vel: Vector2D
                        ) -> PlayerT:
        self_face = float(self_face)
        player = Localizer.PlayerT()
        player.unum_ = seen_player.unum_
        player.goalie_ = seen_player.goalie_
        
        global_dir = float(seen_player.dir_) + self_face
        
        player.rpos_ = Vector2D(r=seen_player.dist_, a=global_dir)
        player.pos_ = self_pos + player.rpos_
        
        if seen_player.has_vel_:
            player.vel_ = Vector2D(seen_player.dist_chng_,
                                   DEG2RAD * seen_player.dir_chng_ * seen_player.dist_)
            player.vel_.rotate(global_dir)
            player.vel_ += self_vel
        else:
            player.vel_.invalidate()
        
        player.has_face_ = False
        if (seen_player.body_  != VisualSensor.DIR_ERR
            and seen_player.face_ != VisualSensor.DIR_ERR):
            
            player.has_face_ = True
            player.body_ = AngleDeg.normalize_angle(seen_player.body_ + self_face)
            player.face_ = AngleDeg.normalize_angle(seen_player.face_ + self_face)
        
        player.pointto_ = False
        if seen_player.arm_ != VisualSensor.DIR_ERR:
            player.pointto_ = True
            player.arm_ = AngleDeg.normalize_angle(seen_player.arm_ + self_face)
        
        player.kicking_ = seen_player.kicking_
        player.tackle_ = seen_player.tackle_

        return player
    
            