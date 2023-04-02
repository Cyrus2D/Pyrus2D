from typing import Union
from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.math_values import DEG2RAD
from pyrusgeom.vector_2d import Vector2D
from pyrusgeom.sector_2d import Sector2D

from lib.debug.debug import log
from lib.player.object_table import ObjectTable, DataEntry
from lib.rcsc.types import UNUM_UNKNOWN, LineID, MarkerID, SideID
from lib.rcsc.server_param import ServerParam
from lib.player.sensor.visual_sensor import SeeParser
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
            self.dist_error_: float = 0.0
        
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

        def __repr__(self):
            return f'PlayerT side:{self.side_} unum:{self.unum_} pos:{self.pos_}'
    
    def __init__(self) -> None:
        self._object_table = ObjectTable()
        self._landmark_map: dict[MarkerID, Vector2D] = {}
        self._points: list[Vector2D] = []

    def get_face_dir_by_markers(self, markers: list[SeeParser.MarkerT], view_width: ViewWidth):
        # TODO This function can be improved by using more than two markers to reduce face error
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
    
    def get_face_dir_by_line(self, lines: list[SeeParser.LineT]):
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
    
    def estimate_self_face(self, see: SeeParser, view_width: ViewWidth):
        face = self.get_face_dir_by_line(see.lines())
        if face is None:
            face = self.get_face_dir_by_markers(see.markers(), view_width)
        
        if Localizer.DEBUG:
            log.sw_log().world().add_text( f"(estimate self face) face={face}")

        face_error = 0.5
        return face, face_error

    def localize_self_simple(self, see:SeeParser, self_face:float):
        if Localizer.DEBUG:
            log.sw_log().world().add_text( f"(localize self) started {'#'*20}")
            

        markers = see.markers() + see.behind_markers()
        markers.sort(key=lambda x: x.dist_)
        
        if len(markers) == 0:
            return None
        
        pos: Vector2D = Vector2D(0,0)
        n_consider = 0
        for marker in markers:
            if n_consider >= 5:
                continue
            if marker.id_ is SeeParser.ObjectType.Obj_Unknown:
                continue
            marker_pos = self._object_table.landmark_map[marker.id_]

            if Localizer.DEBUG:
                log.sw_log().world().add_text( f"(localize self) considered-marker[{marker.id_}]={marker_pos}")
                log.sw_log().world().add_circle( center=marker_pos, r=0.25, fill=True, color=Color(string="black"))

            
            global_dir = marker.dir_ + self_face
            estimated_pos = marker_pos - Vector2D(r=marker.dist_, a=global_dir)
            
            if Localizer.DEBUG:
                log.sw_log().world().add_text( f"(localize self) estimated-pos={estimated_pos}")
                log.sw_log().world().add_circle( center=estimated_pos, r=0.25, fill=True, color=Color(string="red"))
            
            pos += estimated_pos
            n_consider += 1

        if n_consider == 0:
            return None
        pos /= n_consider

        if Localizer.DEBUG:
            log.sw_log().world().add_text( f"(localize self) pos={pos}")
            log.sw_log().world().add_circle( center=pos, r=0.25, fill=True, color=Color(string="blue"))
        
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

    def average_points(self) -> tuple[Union[None, Vector2D], Vector2D]:
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

    def get_nearest_marker(self, object_type: SeeParser.ObjectType, pos: Vector2D):
        if object_type == SeeParser.ObjectType.Obj_Goal_Behind:
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

    def localize_self(self, see: SeeParser, view_width: ViewWidth, self_face: float, self_face_error: float):
        markers = see.markers()
        markers.sort(key=lambda x: x.dist_)

        behind_markers = see.behind_markers()
        behind_markers.sort(key=lambda x: x.dist_)

        if len(markers) == 0:
            return None, Vector2D(0, 0), [None]
        self._points.clear()
        self.generate_points(view_width, markers[0], markers[0].id_, self_face, self_face_error)
        if len(self._points) == 0:
            return None, Vector2D(0, 0), [None]
        self.update_points_by_markers(view_width, markers, self_face, self_face_error)
        self_pos, self_pos_err = self.average_points()
        possible_self_pos = [self_pos.copy() if isinstance(self_pos, Vector2D) else None]
        if len(behind_markers) == 0:
            return self_pos, self_pos_err, possible_self_pos

        self.update_points_by_behind_marker(view_width, markers, behind_markers, self_pos, self_face, self_face_error)
        self_pos, self_pos_err = self.average_points()
        possible_self_pos = [self_pos.copy() if isinstance(self_pos, Vector2D) else None]
        return self_pos, self_pos_err, possible_self_pos

    def localize_ball_relative(self,
                               see: SeeParser,
                               self_face: float,
                               self_face_err: float,
                               view_width: ViewWidth) -> tuple[Vector2D, Vector2D, Vector2D, Vector2D]:
        rpos = Vector2D().invalid()
        rpos_err = Vector2D(0, 0)
        rvel = Vector2D().invalid()
        rvel_err = Vector2D(0, 0)
        self_face = float(self_face)
        if Localizer.DEBUG:
            log.sw_log().world().add_text( f"(localize ball relative) started {'#'*20}")

        if len(see.balls()) == 0:
            return rpos, rpos_err, rvel, rvel_err

        ball = see.balls()[0]
        average_dist, dist_error = self._object_table.get_distance_range(view_width, ball.dist_)
        average_dir, dir_error = self.get_dir_range(ball.dir_, self_face, self_face_err)
        max_dist = average_dist + dist_error
        min_dist = average_dist - dist_error
        max_ang = average_dir + dir_error
        min_ang = average_dir - dir_error
        ave_cos = AngleDeg.cos_deg(average_dir)
        ave_sin = AngleDeg.sin_deg(average_dir)
        rpos.set_x_y(average_dist * ave_cos, average_dist * ave_sin)
        rpos.validate()
        mincos = AngleDeg.cos_deg(average_dir - dir_error)
        maxcos = AngleDeg.cos_deg(average_dir + dir_error)
        minsin = AngleDeg.sin_deg(average_dir - dir_error)
        maxsin = AngleDeg.sin_deg(average_dir + dir_error)

        x1 = max_dist * mincos
        x2 = max_dist * maxcos
        x3 = min_dist * mincos
        x4 = min_dist * maxcos
        y1 = max_dist * minsin
        y2 = max_dist * maxsin
        y3 = min_dist * minsin
        y4 = min_dist * maxsin
        tmp_x = (max(max(x1, x2), max(x3, x4)) - min(min(x1, x2), min(x3, x4))) * 0.5
        tmp_y = (max(max(y1, y2), max(y3, y4)) - min(min(y1, y2), min(y3, y4))) * 0.5
        rpos_err.set_x_y(tmp_x, tmp_y)
        rpos_err.validate()

        if ball.has_vel_:
            ball_dist = max(ball.dist_, 0.00001)
            max_dist_dist_chg1 = (ball.dist_chng_ / ball_dist + 0.02 * 0.5) * max_dist
            max_dist_dist_chg2 = (ball.dist_chng_ / ball_dist - 0.02 * 0.5) * max_dist
            min_dist_dist_chg1 = (ball.dist_chng_ / ball_dist + 0.02 * 0.5) * min_dist
            min_dist_dist_chg2 = (ball.dist_chng_ / ball_dist - 0.02 * 0.5) * min_dist
            max_dir_chg = ball.dir_chng_ + (0.1 * 0.5)
            min_dir_chg = ball.dir_chng_ - (0.1 * 0.5)
            max_dist_dir_chg_r1 = DEG2RAD * max_dir_chg * max_dist
            max_dist_dir_chg_r2 = DEG2RAD * min_dir_chg * max_dist
            min_dist_dir_chg_r1 = DEG2RAD * max_dir_chg * min_dist
            min_dist_dir_chg_r2 = DEG2RAD * min_dir_chg * min_dist

            rvel1_1 = Vector2D(max_dist_dist_chg1, max_dist_dir_chg_r1)
            rvel1_1.rotate(max_ang)
            rvel1_2 = Vector2D(max_dist_dist_chg1, max_dist_dir_chg_r1)
            rvel1_2.rotate(min_ang)
            rvel2_1 = Vector2D(max_dist_dist_chg1, max_dist_dir_chg_r2)
            rvel2_1.rotate(max_ang)
            rvel2_2 = Vector2D(max_dist_dist_chg1, max_dist_dir_chg_r2)
            rvel2_2.rotate(min_ang)
            rvel3_1 = Vector2D(max_dist_dist_chg2, max_dist_dir_chg_r1)
            rvel3_1.rotate(max_ang)
            rvel3_2 = Vector2D(max_dist_dist_chg2, max_dist_dir_chg_r1)
            rvel3_2.rotate(min_ang)
            rvel4_1 = Vector2D(max_dist_dist_chg2, max_dist_dir_chg_r2)
            rvel4_1.rotate(max_ang)
            rvel4_2 = Vector2D(max_dist_dist_chg2, max_dist_dir_chg_r2)
            rvel4_2.rotate(min_ang)
            rvel5_1 = Vector2D(min_dist_dist_chg1, min_dist_dir_chg_r1)
            rvel5_1.rotate(max_ang)
            rvel5_2 = Vector2D(min_dist_dist_chg1, min_dist_dir_chg_r1)
            rvel5_2.rotate(min_ang)
            rvel6_1 = Vector2D(min_dist_dist_chg1, min_dist_dir_chg_r2)
            rvel6_1.rotate(max_ang)
            rvel6_2 = Vector2D(min_dist_dist_chg1, min_dist_dir_chg_r2)
            rvel6_2.rotate(min_ang)
            rvel7_1 = Vector2D(min_dist_dist_chg2, min_dist_dir_chg_r1)
            rvel7_1.rotate(max_ang)
            rvel7_2 = Vector2D(min_dist_dist_chg2, min_dist_dir_chg_r1)
            rvel7_2.rotate(min_ang)
            rvel8_1 = Vector2D(min_dist_dist_chg2, min_dist_dir_chg_r2)
            rvel8_1.rotate(max_ang)
            rvel8_2 = Vector2D(min_dist_dist_chg2, min_dist_dir_chg_r2)
            rvel8_2.rotate(min_ang)

            max_x = max(max(max(max(rvel1_1.x(), rvel1_2.x()), max(rvel2_1.x(), rvel2_2.x())),
                            max(max(rvel3_1.x(), rvel3_2.x()), max(rvel4_1.x(), rvel4_2.x()))),
                        max(max(max(rvel5_1.x(), rvel5_2.x()), max(rvel6_1.x(), rvel6_2.x())),
                            max(max(rvel7_1.x(), rvel7_2.x()), max(rvel8_1.x(), rvel8_2.x()))))
            max_y = max(max(max(max(rvel1_1.y(), rvel1_2.y()), max(rvel2_1.y(), rvel2_2.y())),
                            max(max(rvel3_1.y(), rvel3_2.y()), max(rvel4_1.y(), rvel4_2.y()))),
                        max(max(max(rvel5_1.y(), rvel5_2.y()), max(rvel6_1.y(), rvel6_2.y())),
                            max(max(rvel7_1.y(), rvel7_2.y()), max(rvel8_1.y(), rvel8_2.y()))))

            min_x = min(min(min(min(rvel1_1.x(), rvel1_2.x()), min(rvel2_1.x(), rvel2_2.x())),
                            min(min(rvel3_1.x(), rvel3_2.x()), min(rvel4_1.x(), rvel4_2.x()))),
                        min(min(min(rvel5_1.x(), rvel5_2.x()), min(rvel6_1.x(), rvel6_2.x())),
                            min(min(rvel7_1.x(), rvel7_2.x()), min(rvel8_1.x(), rvel8_2.x()))))
            min_y = min(min(min(min(rvel1_1.y(), rvel1_2.y()), min(rvel2_1.y(), rvel2_2.y())),
                            min(min(rvel3_1.y(), rvel3_2.y()), min(rvel4_1.y(), rvel4_2.y()))),
                        min(min(min(rvel5_1.y(), rvel5_2.y()), min(rvel6_1.y(), rvel6_2.y())),
                            min(min(rvel7_1.y(), rvel7_2.y()), min(rvel8_1.y(), rvel8_2.y()))))

            ave_rvel = rvel1_1.copy()
            ave_rvel += rvel1_2
            ave_rvel += rvel2_1
            ave_rvel += rvel2_2
            ave_rvel += rvel3_1
            ave_rvel += rvel3_2
            ave_rvel += rvel4_1
            ave_rvel += rvel4_2
            ave_rvel += rvel5_1
            ave_rvel += rvel5_2
            ave_rvel += rvel6_1
            ave_rvel += rvel6_2
            ave_rvel += rvel7_1
            ave_rvel += rvel7_2
            ave_rvel += rvel8_1
            ave_rvel += rvel8_2

            ave_rvel /= 16.0

            rvel = ave_rvel.copy()
            rvel.validate()
            rvel_err.assign((max_x - min_x) * 0.5, (max_y - min_y) * 0.5)
            rvel_err.validate()
        return rpos, rpos_err, rvel, rvel_err

    def localize_player(self,
                        seen_player: SeeParser.PlayerT,
                        self_face: float,
                        self_face_err: float,
                        self_pos: Vector2D,
                        self_vel: Vector2D,
                        view_width: ViewWidth
                        ) -> PlayerT:
        self_face = float(self_face)

        average_dist, dist_error = self._object_table.get_distance_range(view_width, seen_player.dist_)
        average_dir, dir_error = self.get_dir_range(seen_player.dir_, self_face, self_face_err)

        player = Localizer.PlayerT()
        player.unum_ = seen_player.unum_
        player.goalie_ = seen_player.goalie_
        player.rpos_._x = average_dist * AngleDeg.cos_deg(average_dir)
        player.rpos_._y = average_dist * AngleDeg.sin_deg(average_dir)
        player.dist_error_ = dist_error
        player.pos_ = self_pos + player.rpos_

        if seen_player.has_vel_:
            player.vel_ = Vector2D(seen_player.dist_chng_,
                                   DEG2RAD * seen_player.dir_chng_ * seen_player.dist_)
            player.vel_.rotate(average_dir)
            player.vel_ += self_vel
        else:
            player.vel_.invalidate()
        
        player.has_face_ = False
        if (seen_player.body_ != SeeParser.DIR_ERR
                and seen_player.face_ != SeeParser.DIR_ERR):
            player.has_face_ = True
            player.body_ = AngleDeg.normalize_angle(seen_player.body_ + self_face)
            player.face_ = AngleDeg.normalize_angle(seen_player.face_ + self_face)
        
        player.pointto_ = False
        if seen_player.arm_ != SeeParser.DIR_ERR:
            player.pointto_ = True
            player.arm_ = AngleDeg.normalize_angle(seen_player.arm_ + self_face)
        
        player.kicking_ = seen_player.kicking_
        player.tackle_ = seen_player.tackle_

        return player
    
            