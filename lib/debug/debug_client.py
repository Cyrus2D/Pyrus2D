from pyrusgeom.geom_2d import *
import socket

from lib.rcsc.types import Card, SideID, GameModeType, UNUM_UNKNOWN

import team_config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.object_player import PlayerObject


def player_printer(p: 'PlayerObject', our_side: SideID):
    s = ' ('

    if p.side() is SideID.NEUTRAL:
        s += 'u'
    elif p.side() == our_side:
        if p.unum() != UNUM_UNKNOWN:
            s += f"t {p.unum()}"
            if p.player_type():
                s += f" {p.player_type().id()}"
            else:
                s += ' -1'
        else:
            s += 'ut'
    else:
        if p.unum() != UNUM_UNKNOWN:
            s += f"o {p.unum()}"
            if p.player_type():
                s += f" {p.player_type().id()}"
            else:
                s += ' -1'
        else:
            s += 'uo'

    s += f" {round(p.pos().x(), 2)} {round(p.pos().y(), 2)}"
    if p.body_valid():
        s += f" (bd {round(p.body().degree())})"

    if p.pointto_count() < 10:
        s += f"(pt {round(float(p.pointto_angle()))})"

    s += ")"
    return s

class DebugClient:
    MAX_LINE = 50       # maximum number of lines in one message.
    MAX_TRIANGLE = 50   # maximum number of triangles in one message.
    MAX_RECT = 50       # maximum number of rectangles in one message.
    MAX_CIRCLE = 50     # maximum number of circles in one message.

    def __init__(self):
        self._on = True
        self._connected = True
        self._socket = self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ip = team_config.HOST
        self._port = team_config.DEBUG_CLIENT_PORT

        self._server_log = None

        self._write_mode = None

        self._main_buffer = ''

        self._target_unum = 0
        self._target_point: Vector2D = Vector2D.invalid()
        self._message = ''

        self._lines = []
        self._triangles = []
        self._rectangles = []
        self._circles = []

    def connect(self, hostname=team_config.HOST, port=team_config.DEBUG_CLIENT_PORT):
        pass

    def open(self, log_dir, teamname, unum):
        pass

    def write_all( self, world, effector):
        self.to_str(world, effector)
        self.send()
        self.clear()

    def close(self):
        pass

    def to_str( self, world: 'WorldModel', effector ):
        ostr = ''
        if world.game_mode().type() is GameModeType.BeforeKickOff:
            ostr = f'((debug (format-version 5)) (time {str(world.time().cycle())},0)'
        else:
            ostr = f'((debug (format-version 5)) (time {str(world.time().cycle())},{world.time().stopped_cycle()})'

        ostr_player = ''
        ostr_ball = ''
        if world.self() and world.self().pos().is_valid():
            ostr_player = ' (s ' \
                          + ('l ' if world.our_side() == SideID.LEFT else 'r ') \
                          + str(world.self().unum()) + ' ' \
                          + str(world.self().player_type_id()) + ' ' \
                          + str(round(world.self().pos().x(), 2)) + ' ' \
                          + str(round(world.self().pos().y(), 2)) + ' ' \
                          + str(round(world.self().vel().x(), 2)) + ' ' \
                          + str(round(world.self().vel().y(), 2)) + ' ' \
                          + str(round(world.self().body().degree(), 1)) + ' ' \
                          + str(round(world.self().neck().degree(), 1)) \
                          + ' (c "' + str(world.self().pos_count()) + ' ' \
                          + str(world.self().vel_count()) + ' ' + str(world.self().face_count())
            if world.self().card() == Card.YELLOW:
                ostr_player += 'y'
            ostr_player += '"))'

        if world.ball().pos().is_valid():
            ostr_ball = ' (b ' + str(round(world.ball().pos().x(), 2)) \
                        + ' ' + str(round(world.ball().pos().y(), 2))
            if world.ball().vel_valid():
                    ostr_ball += (' ' + str(round(world.ball().vel().x(), 2))
                                  + ' ' + str(round(world.ball().vel().y(), 2)))
            ostr_ball += (' (c \'g' + str(world.ball().pos_count()) + 'r'
                          + str(world.ball().rpos_count()) + 'v'
                          + str(world.ball().vel_count())) + '\'))'

        ostr += ostr_player
        ostr += ostr_ball

        for p in world.teammates():
            ostr += player_printer(p, world.our_side())

        for p in world.opponents():
            ostr += player_printer(p, world.our_side())

        if self._target_unum != 0:
            ostr += (' (target-teammate ' + str(self._target_unum)+ ')')

        if self._target_point.is_valid():
            ostr += (' (target-point ' + str(self._target_point.x())
                     + ' ' + str(self._target_point.y()) + ')')

        if self._message != '':
            ostr += (' (message \"' + self._message + '\")')

        for obj in self._lines: obj.to_str(ostr)
        for obj in self._triangles: obj.to_str(ostr)
        for obj in self._rectangles: obj.to_str(ostr)
        for obj in self._circles: obj.to_str(ostr)

        ostr += ')'
        self._main_buffer = ostr

    def send(self):
        if self._main_buffer[-1] != '\0':
            self._main_buffer += '\0'
        self._sock.sendto(self._main_buffer.encode(), (self._ip, self._port))

    def write( self, cycle ):
        pass

    def clear(self):
        self._main_buffer = ''
        self._target_unum = 0
        self._target_point = Vector2D.invalid()
        self._message = ''
        self._lines = []
        self._triangles = []
        self._rectangles = []
        self._circles = []

    def add_message( self, msg):
        self._message += msg

    def set_target(self, unum_or_position):
        if type(unum_or_position) == int:
            self._target_unum = unum_or_position
        else:
            self._target_point = unum_or_position

    def add_line(self, start, end):
        if len(self._lines) < DebugClient.MAX_LINE:
            self._lines.append(Line2D(start, end))

    def add_triangle(self, v1=None, v2=None, v3=None, tri=None):
        if len(self._triangles) < DebugClient.MAX_TRIANGLE:
            if tri:
                self._triangles.append(tri)
            else:
                self._triangles.append(Triangle2D(v1, v2, v3))

    def add_rectangle(self, rect):
        if len(self._rectangles) < DebugClient.MAX_RECT:
            self._rectangles.append(rect)

    def add_circle(self, center=None, radius=None, circle=None):
        if len(self._circles) < DebugClient.MAX_CIRCLE:
            if circle:
                self._circles.append(circle)
            else:
                self._circles.append(Circle2D(center, radius))
