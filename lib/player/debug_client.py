from lib.math.geom_2d import *
import socket
from lib.player.templates import *

# TODO add player
# class PlayerPrinter {
# private:
#     std::ostream & M_os;
#     const char M_tag;
# public:
#     PlayerPrinter( std::ostream & os,
#                      const char tag )
#         : M_os( os )
#         , M_tag( tag )
#       { }
#
#     void operator()( const PlayerObject & p )
#       {
#           M_os << " (";
#           if ( p.unum() != Unum_Unknown )
#           {
#               M_os << M_tag << ' ' << p.unum();
#           }
#           else if ( M_tag == 'u' )
#           {
#               M_os << M_tag;
#           }
#           else
#           {
#               M_os << 'u' << M_tag;
#           }
#
#           M_os << ' ' << ROUND( p.pos().x, 0.01 )
#                << ' ' << ROUND( p.pos().y, 0.01 );
#
#           if ( p.bodyValid() )
#           {
#               M_os << " (bd " << rint( p.body().degree() )
#                    << ')';
#           }
#
#           M_os << " (c \"";
#
#           if  ( p.goalie() )
#           {
#               M_os << "G:";
#           }
#
#           if ( p.unum() != Unum_Unknown )
#           {
#               M_os << 'u' << p.unumCount();
#           }
#
#           M_os << 'p' << p.posCount()
#                << 'v' << p.velCount();
#
#           if ( p.velCount() <= 100 )
#           {
#               M_os << '(' << ROUND( p.vel().x, 0.1 )
#                    << ' ' << ROUND( p.vel().y, 0.1 )
#                    << ')';
#           }
#           M_os << 'f' << p.faceCount();
#
#           if ( p.isTackling() )
#           {
#               M_os << "t";
#           }
#           else if ( p.kicked() )
#           {
#               M_os << "k";
#           }
#
#           if ( p.card() == YELLOW )
#           {
#               M_os << "y";
#           }
#
#           M_os << "\"))";
#       }
# };


class DebugClient:
    MAX_LINE = 50       # maximum number of lines in one message.
    MAX_TRIANGLE = 50   # maximum number of triangles in one message.
    MAX_RECT = 50       # maximum number of rectangles in one message.
    MAX_CIRCLE = 50     # maximum number of circles in one message.

    def __init__(self):
        self._on = True
        self._connected = True
        self._socket = self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ip = 'localhost'
        self._port = 6032

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

    def connect(self, hostname='localhost', port=6032):
        pass

    def open(self, log_dir, teamname, unum):
        pass

    def write_all( self, world, effector):
        self.to_str(world, effector)
        self.send()
        self.clear()

    def close(self):
        pass

    def to_str( self, world: WorldModel, effector ):
        ostr = '((debug (format-version 3)) (time ' + str(world.time().cycle()) + ')'
        ostr_player = ''
        ostr_ball = ''
        if world.self() and world.self().pos().is_valid():
            ostr_player = ' (s ' + ('l ' if world.our_side() == SideID.LEFT else 'r ') + str(world.self().unum()) \
                          + ' ' + str(round(world.self().pos().x(), 2)) + ' ' \
                          + str(round(world.self().pos().y(), 2)) + ' ' \
                          + str(round(world.self().vel().x(), 2)) + ' ' \
                          + str(round(world.self().vel().y(), 2)) + ' ' \
                          + str(round(world.self().body().degree(), 1)) + ' ' \
                          + str(round(world.self().neck().degree(), 1)) \
                          + ' (c \'' + str(world.self().pos_count()) + ' ' \
                          + str(world.self().vel_count()) + ' ' + str(world.self().face_count())
            if world.self().card() == Card.YELLOW:
                ostr_player += 'y'
            ostr_player += '\"))'

        if world.ball().pos().is_valid():
            ostr_ball = ' (b ' + str(round(world.ball().pos().x(), 2)) \
                        + ' ' + str(round(world.ball().pos().y(), 2))
            if world.ball().velValid():
                    ostr_ball += (' ' + str(round(world.ball().vel().x(), 2))
                                  + ' ' + str(round(world.ball().vel().y(), 2)))
            ostr_ball += (' (c \'g' + str(world.ball().pos_count()) + 'r'
                          + str(world.ball().rpos_count()) + 'v'
                          + str(world.ball().vel_count())) + '\'))'

        ostr += ostr_player
        ostr += ostr_ball

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
