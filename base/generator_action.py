from lib.math.geom_2d import *
from lib.player.templates import *


class KickActionType(Enum):
    No = 0
    Pass = 'Pass'
    Dribble = 'Dribble'


class KickAction:
    def __init__(self):
        self.target_ball_pos = Vector2D.invalid()
        self.start_ball_pos = Vector2D.invalid()
        self.target_unum = 0
        self.start_unum = 0
        self.start_ball_speed = 0
        self.type = KickActionType.No
        self.eval = -1000
        self.index = 0

    def evaluate(self):
        self.eval = self.target_ball_pos.x() + max(0, 40 - self.target_ball_pos.dist(Vector2D(52, 0)))

    def __gt__(self, other):
        return self.eval > other.eval

    def __repr__(self):
        return '{} Action {} to {} in {} eval:{}'.format(self.type.value, self.start_unum, self.target_unum, self.target_ball_pos, self.eval)

    def __str__(self):
        return self.__repr__()


class ShootAction:
    def __init__(self, index, target_point, first_ball_speed, ball_move_angle, ball_move_dist, ball_reach_step):
        self.index = index
        self.target_point: Vector2D = target_point
        self.first_ball_vel: Vector2D = Vector2D.polar2vector(first_ball_speed, ball_move_angle)
        self.first_ball_speed = first_ball_speed
        self.ball_move_angle: AngleDeg = ball_move_angle
        self.ball_move_dist = ball_move_dist
        self.ball_reach_step = ball_reach_step
        self.goalie_never_reach = True
        self.opponent_never_reach = True
        self.kick_step = 3
        self.score = 0

    def __repr__(self):
        return '{} target {} first_vel {}'.format(self.index, self.target_point, self.first_ball_vel)

    def __str__(self):
        return self.__repr__()


class BhvKickGen:
    def __init__(self):
        self.candidates = []
        self.index = 0
        self.debug_list = []

    def can_opponent_cut_ball(self, wm: WorldModel, ball_pos, cycle):
        for unum in range(1, 12):
            opp: PlayerObject = wm.their_player(unum)
            if opp.unum() == 0:
                continue
            opp_cycle = opp.pos().dist(ball_pos) - opp.player_type().kickable_area()
            opp_cycle /= opp.player_type().real_speed_max()
            if opp_cycle < cycle:
                return True
        return False
