from turtle import pos
from lib.action.intercept_table import InterceptTable
from lib.debug.debug import log
from lib.player.localizer import Localizer
from lib.messenger.messenger import Messenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.player.object_player import *
from lib.player.object_ball import *
from lib.parser.parser_message_fullstate_world import FullStateWorldMessageParser
from lib.player.object_self import SelfObject
from lib.player.sensor.body_sensor import SenseBodyParser
from lib.player.sensor.visual_sensor import SeeParser
from lib.player.view_area import ViewArea
from lib.player_command.player_command_support import PlayerAttentiontoCommand
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.types import HETERO_DEFAULT, UNUM_UNKNOWN, GameModeType
from pyrusgeom.soccer_math import *
from typing import List


DEBUG=True


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.action_effector import ActionEffector
    

def player_accuracy_value(p: PlayerObject):
    value: int = 0
    if p.goalie():
        value += -1000
    elif p.unum() == UNUM_UNKNOWN:
        value += 1000
    value += p.pos_count() + p.ghost_count() * 10
    return value

def player_count_value(p: PlayerObject):
    return p.pos_count() + p.ghost_count() * 10

def player_valid_check(p: PlayerObject):
    return p.pos_valid()

class WorldModel:
    DEBUG = True
    
    DIR_CONF_DIVS = 72
    DIR_STEP = 360. / DIR_CONF_DIVS
    
    def __init__(self, name):
        self._name = name
        self._is_full_state = True if name == 'full' else False
        self._player_types = [PlayerType() for _ in range(18)]
        self._self_unum: int = None
        self._team_name: str = ""
        self._our_side: SideID = SideID.NEUTRAL
        self._our_players_array:list[PlayerObject] = [None for _ in range(12)]
        self._their_players_array:list[PlayerObject] = [None for _ in range(12)]
        self._their_players:list[PlayerObject] = []
        self._our_players:list[PlayerObject] = []

        self._teammates_from_ball: list[PlayerObject] = []
        self._opponents_from_ball: list[PlayerObject] = []
        self._teammates_from_self: list[PlayerObject] = []
        self._opponents_from_self: list[PlayerObject] = []
        
        self._unknown_players: list[PlayerObject] = []
        
        self._self: SelfObject = SelfObject()
        
        self._ball: BallObject = BallObject()
        self._prev_ball: BallObject = None
        
        self._intercept_table: InterceptTable = InterceptTable()
        self._game_mode: GameMode = GameMode(game_mode=GameModeType.BeforeKickOff)
        self._our_goalie_unum: int = UNUM_UNKNOWN
        self._their_goalie_unum: int = UNUM_UNKNOWN
        self._last_kicker_side: SideID = SideID.NEUTRAL
        self._exist_kickable_teammates: bool = False
        self._exist_kickable_opponents: bool = False
        self._offside_line_x: float = 0
        self._offside_line_count = 0
        self._their_defense_line_x: float = 0
        self._their_defense_line_count = 0
        
        self._previous_kickable_teammate: bool = False
        self._previous_kickable_teammate_unum: int = UNUM_UNKNOWN
        self._kickable_teammate: PlayerObject = None
        self._previous_kickable_opponent: bool = False
        self._previous_kickable_opponent_unum: int = UNUM_UNKNOWN
        self._kickable_opponent: PlayerObject = None
        self._maybe_kickable_teammate: PlayerObject = None
        self._maybe_kickable_opponent: PlayerObject = None
        
        self._teammates: list[PlayerObject] = []
        self._opponents: list[PlayerObject] = []
        
        self._localizer: Localizer = Localizer()
        
        self._time: GameTime = GameTime()
        self._sense_body_time: GameTime = GameTime()
        self._see_time: GameTime = GameTime()
        self._decision_time: GameTime = GameTime()
        
        self._our_team_name: str = None
        self._their_team_name: str = None
        
        self._our_players_type: list[int] = [HETERO_DEFAULT for _ in range(11)]
        self._their_players_type: list[int] = [HETERO_DEFAULT for _ in range(11)]

        self._our_card: list[Card] = [Card.NO_CARD for _ in range(11)]
        self._their_card: list[Card] = [Card.NO_CARD for _ in range(11)]

        self._last_set_play_start_time: GameTime = GameTime()
        self._set_play_count: int = 0
        
        self._our_recovery: list[float] = [1 for _ in range(11)]
        self._our_stamina_capacity: list[float] = [ServerParam.i().stamina_capacity() for _ in range(11)]
        
        self._all_players: list[PlayerObject] = []
        
        self._messenger_memory: MessengerMemory = MessengerMemory()

        self._dir_count:list[int] = [1000 for _ in range(WorldModel.DIR_CONF_DIVS)] 
        
    def init(self,
             team_name: str,
             side: SideID,
             unum: int,
             is_goalie: bool):
        self._our_team_name = team_name
        self._our_side = side
        if is_goalie:
            self._our_goalie_unum = unum
        
        self.self().init(side, unum, is_goalie)
        self.self().set_player_type(self._player_types[HETERO_DEFAULT])
        self._self_unum = unum

    def ball(self) -> BallObject:
        return self._ball

    def self(self) -> SelfObject:
        return self._self

    def our_side(self):
        return SideID.RIGHT if self._our_side == 'r' else SideID.LEFT if self._our_side == 'l' else SideID.NEUTRAL

    def our_player(self, unum):
        if 1 <= unum <= 11:
            return self._our_players_array[unum]
        return None

    def their_player(self, unum):
        if 1 <= unum <= 11:
            return self._their_players_array[unum]
        return None

    def time(self):
        return self._time

    def parse(self, message):
        if 0 < message.find("player_type") < 3:
            self.player_type_parser(message)

    def __repr__(self):
        # Fixed By MM _ temp
        return "(time: {})(ball: {})(tm: {})(opp: {})".format(self._time, self.ball(), self._our_players,
                                                              self._their_players)

    def self_parser(self, message):
        message = message.split(" ")
        self._self_unum = int(message[2])
        self._our_side = message[1]

    def player_type_parser(self, message):
        new_player_type = PlayerType()
        new_player_type.parse(message)
        self._player_types[new_player_type.id()] = new_player_type

    def reverse(self):
        self.ball().reverse()
        Object.reverse_list(self._our_players)
        Object.reverse_list(self._their_players)

    def team_name(self):
        return self._team_name

    def _update_players(self): # TODO Modify it based on teammates and opponent list
        self._exist_kickable_teammates = False
        self._exist_kickable_opponents = False
        for i in range(len(self._our_players)):
            if self._our_players[i].player_type() is None:
                continue
            self._our_players[i].update_with_world(self)
            if self._our_players[i].is_kickable():
                self._last_kicker_side = self.our_side()
                if i != self.self().unum():
                    self._exist_kickable_teammates = True
        for i in range(len(self._their_players)):
            if self._their_players[i].player_type() is None:
                continue
            self._their_players[i].update_with_world(self)
            if self._our_players[i].is_kickable():
                self._last_kicker_side = self._their_players[i].side()
                self._exist_kickable_opponents = True

    def update_offside_line(self):
        if not ServerParam.i().use_offside():
            self._offside_line_count = 0
            self._offside_line_x = ServerParam.i().pitch_half_length()
            return

        if (self._game_mode.type().is_kick_in()
                or self._game_mode.type().is_corner_kick()
                or (self._game_mode.type().is_goal_kick()
                    and self._game_mode.side() == self._our_side)):
            self._offside_line_count = 0
            self._offside_line_x = ServerParam.i().pitch_half_length()
            return

        if (self._game_mode.side() != self._our_side
                and (self._game_mode.type().is_goalie_catch_ball()
                     or self._game_mode.type().is_goal_kick())):
            self._offside_line_count = 0
            self._offside_line_x = ServerParam.i().their_penalty_area_line_x()
            return

        new_line = self._their_defense_line_x
        count = self._their_defense_line_count

        # TODO check audio memory

        self._offside_line_x = new_line
        self._offside_line_count = count

    def update_xx(self): # TODO REMOVE IT
        if self.time().cycle() < 1:
            return  # TODO check
        self._update_players()
        self.ball().update_with_world(self)

        self._set_goalies_unum()  # TODO should it call here?!
        self._set_players_from_ball_and_self()

        # self._update_their_defense_line()
        self.update_offside_line()

        self._intercept_table.update(self)

    def update_their_defense_line(self):
        speed_rate = ServerParam.i().default_player_speed_max() * (0.8
                                                                   if self.ball().vel().x() < -1
                                                                   else 0.25)
        first, second = 0, 0
        first_count, second_count = 1000, 1000

        for it in self._opponents_from_ball:
            x = it.pos().x()
            if it.vel_count() <= 1 and it.vel().x() > 0:
                x += min(0.8, it.vel().x() / it.player_type().player_decay())
            elif it.body_count() <= 3 and it.body().abs() < 100:
                x -= speed_rate * min(10, it.pos_count() - 1.5)
            else:
                x -= speed_rate * min(10, it.pos_count())

            if x > second:
                second = x
                second_count = it.pos_count()
                if second > first:
                    # swap
                    first, second = second, first
                    first_count, second_count = second_count, first_count
        new_line = second
        count = second_count

        goalie = self.get_opponent_goalie()
        if goalie is None:
            if 20 < self.ball().pos().x() < ServerParam.i().their_penalty_area_line_x():
                if first < ServerParam.i().their_penalty_area_line_x():
                    new_line = first
                    count = 30

        if len(self._opponents_from_self) >= 11:
            pass
        elif new_line < self._their_defense_line_x - 13:
            pass
        elif new_line < self._their_defense_line_x - 5:
            new_line = self._their_defense_line_x - 1

        if new_line < 0:
            new_line = 0

        if (self._game_mode.type() == GameModeType.BeforeKickOff
                and self._game_mode.type().is_after_goal()
                and self.ball().pos_count() <= 3):
            ball_next = self.ball().pos() + self.ball().vel()
            if ball_next.x() > new_line:
                new_line = ball_next.x()
                count = self.ball().pos_count()
        self._their_defense_line_x = new_line
        self._their_defense_line_count = count

    def intercept_table(self):
        return self._intercept_table

    def game_mode(self):
        return self._game_mode

    def our_goalie_unum(self):
        return self._our_goalie_unum

    def their_goalie_unum(self):
        return self._their_goalie_unum

    def get_opponent_goalie(self):
        return self.their_player(self._their_goalie_unum)

    def _set_goalies_unum(self):
        for tm in self._our_players:
            if tm is None:
                continue
            if tm.goalie():
                self._our_goalie_unum = tm.unum()
                break

        for opp in self._their_players:
            if opp is None:
                continue
            if opp.goalie():
                self._their_goalie_unum = opp.unum()
                break

    def teammates_from_ball(self):
        return self._teammates_from_ball

    def opponents_from_ball(self):
        return self._opponents_from_ball
    
    def teammates_from_self(self):
        return self._teammates_from_self
    
    def opponents_from_self(self):
        return self._opponents_from_self

    def _set_teammates_from_ball(self):
        self._teammates_from_ball = []
        for tm in self._our_players:
            if tm is None or tm.unum() == self._self_unum:
                continue

            self._teammates_from_ball.append(tm)

        self._teammates_from_ball.sort(key=lambda player: player.dist_from_ball())

    def last_kicker_side(self) -> SideID:
        return self._last_kicker_side
    
    def see_time(self):
        return self._see_time
    
    def sense_body_time(self):
        return self._sense_body_time

    def exist_kickable_opponents(self):
        return self._exist_kickable_opponents

    def exist_kickable_teammates(self):
        return self._exist_kickable_teammates

    def _set_players_from_ball_and_self(self):
        self._set_teammates_from_ball()
        self._set_opponents_from_ball()
        self._set_teammates_from_self()
        self._set_opponents_from_self()

    def _set_teammates_from_self(self):
        self._teammates_from_self = []
        for tm in self._our_players:
            if tm is None or tm.unum() == self._self_unum:
                continue

            self._teammates_from_self.append(tm)

        self._teammates_from_self.sort(key=lambda player: player.dist_from_self())

    def _set_opponents_from_self(self):
        self._opponents_from_self = []
        for opp in self._their_players:
            if opp is None:
                continue

            self._opponents_from_self.append(opp)

        self._opponents_from_self.sort(key=lambda player: player.dist_from_self())

    def _set_opponents_from_ball(self):
        self._opponents_from_ball = []
        for opp in self._their_players:
            if opp is None:
                continue

            self._opponents_from_ball.append(opp)

        self._opponents_from_ball.sort(key=lambda player: player.dist_from_ball())

    def offside_line_x(self) -> float:
        return self._offside_line_x

    def get_opponent_nearest_to_self(self,
                                     count_thr: int,
                                     with_goalie: bool = True) -> PlayerObject:
        return self.get_first_player(self._opponents_from_self,
                                     count_thr,
                                     with_goalie)

    def get_opponent_nearest_to_ball(self, count_thr: int, with_goalie: bool = True):
        return self.get_first_player(self._opponents_from_ball, count_thr, with_goalie)

    def get_teammate_nearest_to_ball(self, count_thr: int, with_goalie: bool = True):
        return self.get_first_player(self._teammates_from_ball, count_thr, with_goalie)

    def get_first_player(self,
                         players: list,
                         count_thr: int,
                         with_goalie: bool) -> PlayerObject:
        for p in players:
            if not with_goalie and p.goalie():
                continue

            if not p.is_ghost() and p.pos_count() <= count_thr:
                return p

        return None

    def self_unum(self):
        return self._self_unum

    def update_by_last_cycle(self, act: 'ActionEffector', agent_current_time: GameTime):
        if self._time == agent_current_time:
            log.os_log().warn(f"(update) player({self.self_unum()}) called twice.")
            return
        
        self._time = agent_current_time.copy()
        self._prev_ball = self._ball.copy()

        self.self().update_by_last_cycle(act, agent_current_time)
        self.ball().update_by_last_cycle(act, self.game_mode())

        self._previous_kickable_teammate = False
        self._previous_kickable_teammate_unum = UNUM_UNKNOWN
        if self._kickable_teammate is not None:
            self._previous_kickable_teammate = True
            self._previous_kickable_teammate_unum = self._kickable_teammate.unum()
            
        self._previous_kickable_opponent = False
        self._previous_kickable_opponent_unum = UNUM_UNKNOWN
        if self._kickable_opponent is not None:
            self._previous_kickable_opponent = True
            self._previous_kickable_opponent_unum = self._kickable_opponent.unum()
        
        self._kickable_teammate = None
        self._kickable_opponent = None
        self._maybe_kickable_teammate = None
        self._maybe_kickable_opponent = None
        
        self._teammates_from_ball.clear()
        self._teammates_from_self.clear()
        self._opponents_from_ball.clear()
        self._opponents_from_self.clear()

        self._all_players.clear()
        self._our_players.clear()
        self._their_players.clear()

        if (self.game_mode().type() == GameModeType.BeforeKickOff
            or (self.game_mode().type().is_after_goal() and self._time.stopped_cycle() <= 48)):
            
            self._teammates.clear()
            self._opponents.clear()
            self._unknown_players.clear()
        
        for p in self._teammates:
            p.update_by_last_cycle()
        self._teammates = list(filter(lambda p: p.pos_count() < 30,self._teammates))

        for p in self._opponents:
            p.update_by_last_cycle()
        self._opponents = list(filter(lambda p: p.pos_count() < 30,self._opponents))
        
        for p in self._unknown_players:
            p.update_by_last_cycle()
        self._unknown_players = list(filter(lambda p: p.pos_count() < 30,self._unknown_players))

        self._dir_count = [c+1 for c in self._dir_count]
    
    def estimate_ball_by_pos_diff(self, see: SeeParser, act: 'ActionEffector', rpos: Vector2D, rpos_error: Vector2D, vel: Vector2D, vel_error: Vector2D, vel_count) -> int:
        SP = ServerParam.i()

        if self.self().has_sensed_collision():
            if self.self()._collides_with_player or self.self()._collides_with_post:
                return 1000
        
        if self.ball().rpos_count() == 1:
            if (see.balls()[0].dist_ < SP.visible_distance()
                    and self._prev_ball.rpos().is_valid()
                    and self.self().vel_valid()
                    and self.self().last_move().is_valid()):
                rpos_diff = rpos - self._prev_ball.rpos()
                tmp_vel = (rpos_diff + self.self().last_move()) * SP.ball_decay()
                tmp_vel_error = rpos_error + self.self().vel_error() * SP.ball_decay()

                if (self.ball().seen_vel_count() <= 2
                        and self._prev_ball.rpos().r() > 1.5
                        and see.balls()[0].dist_ > 1.5
                        and abs(tmp_vel.x() - self.ball().vel().x()) < 0.1
                        and abs(tmp_vel.y() - self.ball().vel().y()) < 0.1):
                    return 1000
                vel.assign(tmp_vel.x(), tmp_vel.y())
                vel_error.assign(tmp_vel_error.x(), tmp_vel_error.y())
                return 1
        
        elif self.ball().rpos_count() == 2:
            if (see.balls()[0].dist_ < SP.visible_distance()
                    and act.last_body_command() is not CommandType.KICK
                    and self.ball().seen_rpos().is_valid()
                    and self.ball().seen_rpos().r() < SP.visible_distance()
                    and self.self().vel_valid()
                    and self.self().last_move(0).is_valid()
                    and self.self().last_move(1).is_valid()):
                ball_move: Vector2D = rpos - self.ball().seen_rpos()
                for i in range(2):
                    ball_move += self.self().last_move(i)
                vel.set_vector(ball_move * ((SP.ball_decay() ** 2) / (1 + SP.ball_decay())))
                vel_r = vel.r()
                estimate_speed = self.ball().vel().r() 
                if (vel_r > estimate_speed + 0.1
                    or vel_r < estimate_speed*(1-SP.ball_rand()*2) - 0.1
                    or (vel - self.ball().vel()).r() > estimate_speed * SP.ball_rand()*2 + 0.1):

                    vel.invalidate()
                    return 1000
                else:
                    vel_error.set_vector((rpos_error * 2.0) + self.self().vel_error())
                    vel_error *= SP.ball_decay()
                    return 2
        
        elif self.ball().rpos_count() == 3:
            if (see.balls()[0].dist_ < SP.visible_distance()
                and act.last_body_command(0) is not CommandType.KICK
                and act.last_body_command(1) is not CommandType.KICK
                and self.ball().seen_rpos().is_valid()
                and self.ball().seen_rpos().r() < SP.visible_distance()
                and self.self().vel_valid()
                and self.self().last_move(0).is_valid()
                and self.self().last_move(1).is_valid()
                and self.self().last_move(2).is_valid()):

                ball_move: Vector2D = rpos - self.ball().seen_rpos()
                for i in range(3):
                    ball_move += self.self().last_move(i)
                vel.set_vector(ball_move * (SP.ball_decay()**3 / (1 + SP.ball_decay() + SP.ball_decay()**2)))
                vel_r = vel.r()
                estimate_speed = self.ball().vel().r()
                if (vel_r > estimate_speed + 0.1
                    or vel_r < estimate_speed*(1-SP.ball_rand()*3) - 0.1
                    or (vel - self.ball().vel()).r() > estimate_speed * SP.ball_rand()*3 + 0.1):

                    vel.invalidate()
                    return 1000
                else:
                    vel_error.set_vector((rpos_error * 3.0) + self.self().vel_error())
                    return 3
        return vel_count
                
    def localize_self(self,
                      see: SeeParser,
                      body: SenseBodyParser,
                      act: 'ActionEffector',
                      current_time: GameTime):
        angle_face, angle_face_error = self._localizer.estimate_self_face(see, self.self().view_width())
        if angle_face is None:
            return False

        reverse_side = self.our_side() == SideID.RIGHT
        team_angle_face = AngleDeg(angle_face + 180.0) if reverse_side else angle_face

        self.self().update_angle_by_see(team_angle_face, angle_face_error, current_time)
        self.self().update_vel_dir_after_see(body, current_time)

        # my_pos: Vector2D = self._localizer.localize_self_simple(see, angle_face)
        my_pos, my_pos_err, my_possible_posses = self._localizer.localize_self(see, self.self().view_width(), angle_face, angle_face_error)
        if my_pos is None:
            return False
        if reverse_side:
            my_pos *= -1.0

        if my_pos.is_valid():
            self.self().update_pos_by_see(my_pos, my_pos_err, my_possible_posses, team_angle_face, angle_face_error, current_time)
        
    def localize_ball(self, see: SeeParser, act: 'ActionEffector'):
        SP = ServerParam.i()
        if not self.self().face_valid():
            return
        
        rpos, rpos_err, rvel, vel_err = self._localizer.localize_ball_relative(see,
                                                                               self.self().face(),
                                                                               self.self().face_error(),
                                                                               self.self().view_width())
        
        if rpos is None or not rpos.is_valid():
            return
        
        if not self.self().pos_valid():
            if (self._prev_ball.rpos_count() == 0
                and see.balls()[0].dist_ > self.self().player_type().player_size() + SP.ball_size() + 0.1
                and self.self().last_move().is_valid()):
                tvel = (rpos - self._prev_ball.rpos()) + self.self().last_move()
                tvel_err = rpos_err + self.self().vel_error()

                tvel *= SP.ball_decay()
                tvel_err *= SP.ball_decay()
                self._ball.update_only_vel(tvel, tvel_err, 1)
            self._ball.update_only_relative_pos(rpos, rpos_err)
            return
        
        pos = self.self().pos() + rpos
        pos_err = self.self().pos_error() + rpos_err
        gvel = Vector2D.invalid()
        vel_count = 1000
        
        if WorldModel.DEBUG:
            log.sw_log().world().add_text( f"(localize ball) rvel_valid={rvel.is_valid()}, self_vel_valid={self.self().vel_valid()}, self_vel_count={self.self().vel_count()}")
            log.sw_log().world().add_text( f"(localize ball) rvel={rvel}, self_vel={self.self().vel()}")
        
        if rvel.is_valid() and self.self().vel_valid():
            gvel = self.self().vel() + rvel
            vel_err += self.self().vel_error()
            vel_count = 0
        
        if not gvel.is_valid():
            vel_count = self.estimate_ball_by_pos_diff(see, act, rpos, rpos_err, gvel, vel_err, vel_count)
        
        if not gvel.is_valid():
            if (see.balls()[0].dist_ < 2
                and self._prev_ball.seen_pos_count() == 0
                and self._prev_ball.rpos_count() == 0
                and self._prev_ball.rpos().r() < 5):

                gvel = pos - self._prev_ball.pos()
                vel_err += pos_err + self._prev_ball._pos_error + self._prev_ball._vel_error
                vel_count = 2
            elif (see.balls()[0].dist_ < 2
                  and not self.self().is_kicking()
                  and 2 <= self._ball.seen_pos_count() <= 6
                  and self.self().last_move(0).is_valid()
                  and self.self().last_move(1).is_valid()):
                prev_pos = self._ball.seen_pos()
                move_step = self._ball.seen_pos_count()
                ball_move: Vector2D = pos - prev_pos
                dist = ball_move.r()
                speed = SP.first_ball_speed(dist, move_step)
                speed = max(speed, SP.ball_speed_max()) * (SP.ball_decay()**move_step)
                gvel = ball_move.set_length_vector(speed)
                vel_count = move_step
        
        if gvel.is_valid():
            self._ball.update_all(pos, pos_err, self.self().pos_count(),
                                  rpos, rpos_err,
                                  gvel, vel_err, vel_count)
        else:
            self._ball.update_pos(pos, pos_err, self.self().pos_count(), rpos, rpos_err)
    
    def their_side(self):
        return SideID.LEFT if self._our_side is SideID.RIGHT else SideID.RIGHT
    
    def check_team_player(self,
                          side: SideID,
                          player: Localizer.PlayerT,
                          old_known_players: list[PlayerObject],
                          old_unknown_players: list[PlayerObject],
                          new_known_players: list[PlayerObject]):

        log.os_log().debug(f'------- check with old known A')
        if player.unum_ != UNUM_UNKNOWN:
            for p in old_known_players:
                log.os_log().debug(f'--------------?? {p}')
                if p.unum() == player.unum_:
                    p.update_by_see(side, player)
                    new_known_players.append(p)
                    old_known_players.remove(p)
                    log.os_log().debug(f'--------------> update {p.unum()}')
                    return
        
        min_team_dist = 1000
        min_unknown_dist = 1000
        candidate_team: Union[None, PlayerObject] = None
        candidate_unknown: Union[None, PlayerObject] = None

        log.os_log().debug(f'------- check with old known B')
        for p in old_known_players:
            log.os_log().debug(f'--------------?? {p}')
            if p.unum() != UNUM_UNKNOWN and player.unum_ != UNUM_UNKNOWN and p.unum() != player.unum_:
                log.os_log().debug(f'--------------<< No (unum)')
                continue
            count = p.seen_pos_count()
            old_pos = p.seen_pos()
            if p.heard_pos_count() < p.seen_pos_count():
                count = p.heard_pos_count()
                old_pos = p.heard_pos()
            
            d = player.pos_.dist(old_pos)
            if d > p.player_type().real_speed_max() * count + player.dist_error_ * 2.0:
                log.os_log().debug(f'--------------<< No (dist)')
                continue
            
            if d < min_team_dist:
                min_team_dist = d
                candidate_team = p
                log.os_log().debug(f'-------------->> update best candid {min_team_dist} {candidate_team}')

        log.os_log().debug(f'------- check with old unknown')
        for p in old_unknown_players:
            if p.unum() != UNUM_UNKNOWN and player.unum_ != UNUM_UNKNOWN and p.unum() != player.unum_:
                log.os_log().debug(f'--------------<< No (unum)')
                continue
            
            count = p.seen_pos_count()
            old_pos = p.seen_pos()
            if p.heard_pos_count() < p.seen_pos_count():
                count = p.heard_pos_count()
                old_pos = p.heard_pos()
            
            d = player.pos_.dist(old_pos)
            if d > p.player_type().real_speed_max() * count + player.dist_error_ * 2.0:
                log.os_log().debug(f'--------------<< No (dist)')
                continue
            
            if d < min_team_dist:
                min_unknown_dist = d
                candidate_unknown = p
                log.os_log().debug(f'-------------->> update best candid {min_unknown_dist} {candidate_unknown}')

        candidate: Union[None, PlayerObject] = None
        target_list: Union[None, list[PlayerObject]] = None
        if candidate_team is not None and min_team_dist < min_unknown_dist:
            candidate = candidate_team
            target_list = old_known_players
            log.os_log().debug('------ >>>> candid in old known')

        if candidate_unknown is not None and min_unknown_dist < min_team_dist:
            candidate = candidate_unknown
            target_list = old_unknown_players
            log.os_log().debug('------ >>>> candid in old unknown')

        if candidate is not None and target_list is not None:
            candidate.update_by_see(side, player)
            log.os_log().debug(f'---> update {candidate.unum()}')
            new_known_players.append(candidate)
            target_list.remove(candidate)
            return
        new_known_players.append(PlayerObject(side=side, player=player))
        log.os_log().debug(f'---> add new known player {new_known_players[-1]}')

    def check_unknown_player(self,
                             player: Localizer.PlayerT,
                             old_teammates: list[PlayerObject],
                             old_opponents: list[PlayerObject],
                             old_unknown_players: list[PlayerObject],
                             new_teammates: list[PlayerObject],
                             new_opponents: list[PlayerObject],
                             new_unknown_players: list[PlayerObject]):
        
        min_opponent_dist = 100
        min_teammate_dist = 100
        min_unknown_dist = 100
        
        candidate_opponent: PlayerObject = None
        candidate_teammate: PlayerObject = None
        candidate_unknown: PlayerObject = None
        
        for p in old_opponents:
            if (p.unum() != UNUM_UNKNOWN
                and player.unum_ != UNUM_UNKNOWN
                and p.unum() != player.unum_):
                continue
            
            count = p.seen_pos_count()
            old_pos = p.seen_pos()
            if p.heard_pos_count() < p.seen_pos_count():
                count = p.heard_pos_count()
                old_pos = p.heard_pos()
            
            d = player.pos_.dist(old_pos)
            if d > p.player_type().real_speed_max() * count:
                continue
            
            if d < min_opponent_dist:
                min_opponent_dist = d
                candidate_opponent = p
        
        for p in old_teammates:
            if (p.unum() != UNUM_UNKNOWN
                and player.unum_ != UNUM_UNKNOWN
                and p.unum() != player.unum_):
                continue
            
            count = p.seen_pos_count()
            old_pos = p.seen_pos()
            if p.heard_pos_count() < p.seen_pos_count():
                count = p.heard_pos_count()
                old_pos = p.heard_pos()
            
            d = player.pos_.dist(old_pos)
            if d > p.player_type().real_speed_max() * count:
                continue
            
            if d < min_teammate_dist:
                min_teammate_dist = d
                candidate_teammate = p

        for p in old_unknown_players:
            if (p.unum() != UNUM_UNKNOWN
                and player.unum_ != UNUM_UNKNOWN
                and p.unum() != player.unum_):
                continue
            
            count = p.seen_pos_count()
            old_pos = p.seen_pos()
            if p.heard_pos_count() < p.seen_pos_count():
                count = p.heard_pos_count()
                old_pos = p.heard_pos()
            
            d = player.pos_.dist(old_pos)
            if d > p.player_type().real_speed_max() * count:
                continue
            
            if d < min_unknown_dist:
                minunk = d
                candidate_unknown = p
        
        candidate: PlayerObject = None
        new_list: list[PlayerObject] = None
        old_list: list[PlayerObject] = None
        side: SideID = SideID.NEUTRAL

        if (candidate_teammate is not None
            and min_teammate_dist < min(min_opponent_dist, min_unknown_dist)):
            candidate = candidate_teammate
            new_list = new_teammates
            old_list = old_teammates
            side = self.our_side()
        
        if (candidate_opponent is not None
            and min_opponent_dist < min(min_teammate_dist, min_unknown_dist)):
            candidate = candidate_opponent
            new_list = new_opponents
            old_list = old_opponents
            side = self.their_side()
        
        if (candidate_unknown is not None
            and min_unknown_dist < min(min_teammate_dist, min_opponent_dist)):
            candidate = candidate_unknown
            new_list = new_unknown_players
            old_list = old_unknown_players
            side = SideID.NEUTRAL
        
        if candidate is not None and new_list is not None and old_list is not None:
            candidate.update_by_see(side, player)
            new_list.append(candidate)
            old_list.remove(candidate)
            return
        
        new_unknown_players.append(PlayerObject(side=SideID.NEUTRAL, player=player))
    
    def localize_players(self, see: SeeParser):
        if not self.self().face_valid() or not self.self().pos_valid():
            return
        if DEBUG:
            log.os_log().debug(f'{"#"*30} Localize players ')
        new_teammates: list[PlayerObject] = []
        new_opponents: list[PlayerObject] = []
        new_unknown_players: list[PlayerObject] = []
        
        my_pos = self.self().pos()
        my_vel = self.self().vel()
        my_face = self.self().face()
        my_face_err = self.self().face_error()

        for p in see.opponents() + see.unknown_opponents():
            player = self._localizer.localize_player(p, my_face, my_face_err, my_pos, my_vel, self.self().view_width())
            if DEBUG:
                log.os_log().debug(f'{"-"*30} opp {player}')
            if player is None:
                continue
            self.check_team_player(self.their_side(),
                                   player,
                                   self._opponents,
                                   self._unknown_players,
                                   new_opponents)
            
        for p in see.teammates() + see.unknown_teammates():
            player = self._localizer.localize_player(p, my_face, my_face_err, my_pos, my_vel, self.self().view_width())
            if DEBUG:
                log.os_log().debug(f'{"-"*30} mate {player}')
            if player is None:
                continue
            self.check_team_player(self.our_side(),
                                   player,
                                   self._teammates,
                                   self._unknown_players,
                                   new_teammates)
        
        for p in see.unknown_players():
            player = self._localizer.localize_player(p, my_face, my_face_err, my_pos, my_vel, self.self().view_width())
            if DEBUG:
                log.os_log().debug(f'{"-"*30} unk {player}')
            if player is None:
                continue
            self.check_unknown_player(player,
                                      self._teammates,
                                      self._opponents,
                                      self._unknown_players,
                                      new_teammates,
                                      new_opponents,
                                      new_unknown_players)
        if DEBUG:
            log.os_log().debug(f'{"#"*30} End Localize players ')
            for t in self._teammates:
                log.os_log().debug(f'old team {t}')
            for t in new_teammates:
                log.os_log().debug(f'new team {t}')
            for t in self._opponents:
                log.os_log().debug(f'old team {t}')
            for t in new_opponents:
                log.os_log().debug(f'new team {t}')
            for t in self._unknown_players:
                log.os_log().debug(f'old unk {t}')
            for t in new_unknown_players:
                log.os_log().debug(f'new unk {t}')
        self._teammates += new_teammates
        self._opponents += new_opponents
        log.os_log().debug(f'opp len {len(self._opponents)} A')
        self._unknown_players += new_unknown_players
        
        all_teammates = sorted(self._teammates, key=player_accuracy_value)
        all_opponents = sorted(self._opponents, key=player_accuracy_value)
        log.os_log().debug(f'opp len {len(self._opponents)} B')
        log.os_log().debug(f'opp len {len(all_opponents)} C')
        self._unknown_players.sort(key=player_count_value)
        
        for p in all_teammates[10:] + all_opponents[11:]:
            log.os_log().debug(f'forget {p}')
            p.forgot()
        log.os_log().debug(f'opp len {len(self._opponents)} D')
        self._teammates = list(filter(player_valid_check, self._teammates))
        self._opponents = list(filter(player_valid_check, self._opponents))
        log.os_log().debug(f'opp len {len(self._opponents)} E')

    def update_player_type(self):
        for p in self._teammates:
            unum = p.unum() - 1
            if 0 <= unum < 11:
                p.set_player_type(self._player_types[self._our_players_type[unum]])
            else:
                p.set_player_type(self._player_types[HETERO_DEFAULT])
        
        for p in self._opponents:
            unum = p.unum() - 1
            if 0 <= unum < 11:
                p.set_player_type(self._player_types[self._their_players_type[unum]])
            else:
                p.set_player_type(self._player_types[HETERO_DEFAULT])
        
        for p in self._unknown_players:
            p.set_player_type(self._player_types[HETERO_DEFAULT]) 

    def update_world_after_see(self,
                               see: SeeParser,
                               body: SenseBodyParser,
                               act: 'ActionEffector',
                               current_time: GameTime):
        
        if self._see_time == current_time: # TODO see time
            return
        
        self._see_time = current_time.copy()
        log.sw_log().world().add_text( f"{'*'*20} Update by See {'*'*20}")
        log.os_log().debug(f"{'#' * 30} Update by See {'#' * 30}")

        if self._their_team_name is None and see.their_team_name() is not None:
            self._their_team_name = see.their_team_name()
            log.sw_log().world().add_text( f"(update after see) their team name set to {self._their_team_name}")
        
        # TODO FULL STATE TIME CHECK
        
        self.localize_self(see, body, act, current_time)
        self.localize_ball(see, act)
        self.localize_players(see)
        self.update_player_type()
        
        if self.self().pos_count() <= 10:
            varea = ViewArea(self.self().view_width().width(),
                             self.self().pos(),
                             self.self().face(),
                             current_time)
            self.check_ghost(varea) # TODO 
            self.update_dir_count(varea)

    def update_world_after_sense_body(self, body_sensor: SenseBodyParser, act: 'ActionEffector', agent_current_time: GameTime):
        if self._sense_body_time == agent_current_time:
            log.os_log().critical(f"({self.team_name()} {self.self().unum()}): update after sense body called twice in a cycle")
            log.sw_log().sensor(f"({self.team_name()} {self.self().unum()}): update after sense body called twice in a cycle")
            return

        self._sense_body_time = body_sensor.time().copy()

        if body_sensor.time() == agent_current_time:
            self.self().update_self_after_sense_body(body_sensor, act, agent_current_time)
            self._our_recovery[self.self().unum() - 1] = self.self().recovery()
            self._our_stamina_capacity[self.self().unum() - 1] = self.self().stamina_model().capacity()
            self._our_card[self.self().unum() - 1] = body_sensor.card()
        else:
            log.os_log().error(f'body_sensor.time()[{body_sensor.time()}] != current_time[{agent_current_time}]')

        if DEBUG:
            log.sw_log().world().add_text("******** update world after sense body ********")
            log.os_log().debug("******** update world after sense body ********")
            log.sw_log().world().add_text(str(self.self()))
            log.os_log().debug(str(self.self()))

    def update_game_mode(self, game_mode: GameMode, current_time: GameTime):
        pk_mode = game_mode.is_penalty_kick_mode()
        if not pk_mode and self._game_mode.type() is not  GameModeType.PlayOn:
            if game_mode.type() != self.game_mode().type():
                self._last_set_play_start_time = current_time.copy()
                self._set_play_count = 0
            
            if game_mode.type().is_goal_kick():
                self._ball.update_only_vel(Vector2D(0, 0), 0)
        SP = ServerParam.i()
        if game_mode.type() is GameModeType.BeforeKickOff:
            normal_time = (SP.actual_half_time() * SP.nr_normal_halfs()
                                if SP.half_time() > 0 and SP.nr_normal_halfs() > 0
                                else 0)
            if current_time.cycle() < normal_time:
                for i in range(11):
                    self._our_recovery[i] = 1
                    self._our_stamina_capacity[i] = SP.stamina_capacity()
            else:
                for i in range(11):
                    self._our_stamina_capacity[i] = SP.stamina_capacity()
        
        self._game_mode = game_mode.copy()
        if pk_mode:
            pass # TODO PENALTY
    
    def create_set_player(self,
                          players: list[PlayerObject],
                          players_from_self: list[PlayerObject],
                          players_from_ball: list[PlayerObject],
                          self_pos: Vector2D,
                          ball_pos: Vector2D):
        for p in players:
            p.update_self_ball_related(self_pos, ball_pos)
            players_from_self.append(p)
            players_from_ball.append(p)
    
    def update_kickables(self):
        for p in self._teammates_from_ball:
            if p.is_ghost() or p.is_tackling() or p.pos_count() > self.ball().pos_count():
                continue
            
            if p.is_kickable(0):
                self._kickable_teammate = p
                break
        for p in self._opponents_from_ball:
            if p.is_ghost() or p.is_tackling() or p.pos_count() >= 10:
                continue
            
            if p.dist_from_ball() > 5:
                break
            
            if p.is_kickable(0):
                self._kickable_opponent = p
                break
        
    
    def update_player_state_cache(self):
        if not self.self().pos_valid() or not self.ball().pos_valid():
            return
        
        self.create_set_player(self._teammates,
                               self._teammates_from_self,
                               self._teammates_from_ball,
                               self.self().pos(),
                               self.ball().pos())
        self.create_set_player(self._opponents,
                               self._opponents_from_self,
                               self._opponents_from_ball,
                               self.self().pos(),
                               self.ball().pos())
        self.create_set_player(self._unknown_players,
                               self._opponents_from_self,
                               self._opponents_from_ball,
                               self.self().pos(),
                               self.ball().pos())
        
        self._teammates_from_ball.sort(key=lambda p: p.dist_from_ball())
        self._opponents_from_ball.sort(key=lambda p: p.dist_from_ball())
        
        self._teammates_from_self.sort(key=lambda p: p.dist_from_self())
        self._opponents_from_self.sort(key=lambda p: p.dist_from_self())
        
        # self.estimate_unknown_player_unum() # TODO IMP FUNC?!
        self.estimate_goalie()

        log.sw_log().world().add_text(f'=== GOALIE UNUM ===')
        log.sw_log().world().add_text(f'our/their goalie: {self._our_goalie_unum}/{self._their_goalie_unum}')


        self._all_players.append(self.self())
        self._our_players.append(self.self())
        for i in range(12):
            self._our_players_array[i] = None
            self._their_players_array[i] = None

        self._our_players_array[self.self().unum()] = self.self()
        for p in self._teammates:
            self._all_players.append(p)
            self._our_players.append(p)
            if p.unum() != UNUM_UNKNOWN:
                self._our_players_array[p.unum()] = p
        for p in self._opponents:
            self._all_players.append(p)
            self._their_players.append(p)
            if p.unum() != UNUM_UNKNOWN:
                self._their_players_array[p.unum()] = p
        
        self.update_kickables()
    
    def estimate_goalie(self):
        our_goalie: PlayerObject = None
        their_goalie: PlayerObject = None

        if self.self().goalie():
            our_goalie = self.self()
        else:
            for p in self._teammates:
                if p.goalie():
                    our_goalie = p
        for p in self._opponents:
            if p.goalie():
                their_goalie = p
        
        if our_goalie and our_goalie.unum() != self.our_goalie_unum():
            self._our_goalie_unum = our_goalie.unum()
        
        if their_goalie and their_goalie.unum() != self._their_goalie_unum:
            self._their_goalie_unum = their_goalie.unum()
        
        if (self.game_mode().type() is GameModeType.BeforeKickOff
            or self.game_mode().type().is_after_goal()):
            return
        
        if our_goalie is None and len(self._teammates) >= 9:
            self.estimate_our_goalie()
        if their_goalie is None and len(self._teammates) >= 10 and len(self._opponents) >= 11:
            self.estimate_their_goalie()
    
    def estimate_their_goalie(self):
        candidate: PlayerObject = None
        max_x: float = 0
        second_max_x: float = 0    
        for p in self._opponents:
            x = p.pos().x()
            
            if x > second_max_x:
                second_max_x = x
                
                if second_max_x > max_x:
                    max_x, second_max_x = second_max_x, max_x
                    candidate = p
        
        from_unknown = False
        for p in self._unknown_players:
            x = p.pos().x()
            
            if x > second_max_x:
                second_max_x = x
                
                if second_max_x > max_x:
                    max_x, second_max_x = second_max_x, max_x
                    candidate = p
                    from_unknown = True
        
        if candidate is not None and second_max_x > max_x - 10:
            candidate.set_team(self.their_side(),
                               self._their_goalie_unum,
                               True)
            
            if from_unknown:
                self._opponents.append(candidate)
                self._unknown_players.remove(candidate)        
    
    def estimate_our_goalie(self):
        candidate: PlayerObject = None
        min_x: float = 0
        second_min_x: float = 0    
        for p in self._teammates:
            x = p.pos().x()
            
            if x < second_min_x:
                second_min_x = x
                
                if second_min_x < min_x:
                    min_x, second_min_x = second_min_x, min_x
                    candidate = p
        
        from_unknown = False
        for p in self._unknown_players:
            x = p.pos().x()
            
            if x < second_min_x:
                second_min_x = x
                
                if second_min_x < min_x:
                    min_x, second_min_x = second_min_x, min_x
                    candidate = p
                    from_unknown = True
        
        if candidate is not None and second_min_x > min_x + 10:
            candidate.set_team(self.our_side(),
                               self._our_goalie_unum,
                               True)
            
            if from_unknown:
                self._teammates.append(candidate)
                self._unknown_players.remove(candidate)

    def update_intercept_table(self):
        self.intercept_table().update(self)

    def update_goalie_by_hear(self):
        SP = ServerParam.i()
        # TODO CHECK FULL STATE TIME
        log.sw_log().world().add_text(f'{"#"*20} UPDATE GOALIE BY HEAR {"#"*20}')

        if self._messenger_memory.goalie_time() != self.time() or len(self._messenger_memory.goalie()) == 0:
            return

        goalie: PlayerObject = None

        for o in self._opponents:
            if o.goalie():
                goalie = o
                break

        if goalie is not None and goalie.pos_count() == 0 and goalie.body_count() == 0:
            return

        heard_pos = Vector2D(0, 0)
        heard_body = 0.

        for g in self._messenger_memory.goalie():
            heard_pos += g.pos_
            heard_body += AngleDeg(g.body_).degree()

        heard_body /= len(self._messenger_memory.goalie())
        heard_pos /= len(self._messenger_memory.goalie())

        if goalie is not None:
            goalie.update_by_hear(self.their_side(), self._their_goalie_unum,True, heard_pos, heard_body)
            log.sw_log().world().add_text(f'(update player by hear) '
                                             f's={self.their_side()} u={self._their_goalie_unum} '
                                             f'p={heard_pos} b={heard_body}')
            return

        goalie_speed_max = SP.default_player_speed_max()
        min_dist = 1000.
        for o in self._opponents + self._unknown_players:
            if o.unum() != UNUM_UNKNOWN:
                continue
            if o.pos().x() < SP.their_penalty_area_line_x() or o.pos().abs_y() > SP.penalty_area_half_width():
                continue

            d = o.pos().dist(heard_pos)
            if d < min_dist and d < o.pos_count() * goalie_speed_max + o.dist_from_self() * 0.06:
                min_dist = d
                goalie = o

        if goalie is not None:
            goalie.update_by_hear(self.their_side(), self._their_goalie_unum, True, heard_pos, heard_body)
            log.sw_log().world().add_text(f'(update player by hear) '
                                             f's={self.their_side()} u={self._their_goalie_unum} '
                                             f'p={heard_pos} b={heard_body}')
        else:
            goalie = PlayerObject()
            self._opponents.append(goalie)
            goalie.update_by_hear(self.their_side(), self._their_goalie_unum, True, heard_pos, heard_body)
            log.sw_log().world().add_text(f'(update player by hear) '
                                             f's={self.their_side()} u={self._their_goalie_unum} '
                                             f'p={heard_pos} b={heard_body}')

    def update_player_stamina_by_hear(self):
        if self._messenger_memory.recovery_time() == self.time():
            for r in self._messenger_memory.recovery():
                if 1 <= r.sender_ <= 11:
                    self._our_recovery[r.sender_ - 1] = r.rate_
                    log.sw_log().world().add_text(f'(update player stamina by hear) u={r.sender_} r={r.rate_}')

        if self._messenger_memory.stamina_time() == self.time():
            for r in self._messenger_memory.stamina():
                if 1 <= r.sender_ <= 11:
                    self._our_stamina_capacity[r.sender_ - 1] = r.rate_
                    log.sw_log().world().add_text(f'(update player stamina by hear) u={r.sender_} s={r.rate_}')

    def update_by_full_state_message(self, parser: FullStateWorldMessageParser):
        self._time._cycle = int(parser.dic()['time'])
        self._game_mode.set_game_mode(GameModeType(parser.dic()['pmode']))

        # TODO vmode counters and arm

        self._ball.init_str(parser.dic()['b'])
        self._teammates.clear()
        self._opponents.clear()
        self._unknown_players.clear()
        self._all_players.clear()
        self._our_players.clear()
        self._their_players.clear()
        for player_dic in parser.dic()['players']:
            player = PlayerObject()
            player.init_dic(player_dic)
            player.set_player_type(self._player_types[player.player_type_id()])
            if player.side().value == self._our_side:
                if player.unum() == self._self_unum:
                    self._self.update_by_player_info(player)
                else:
                    self._teammates.append(player)
            elif player.side() == SideID.NEUTRAL:
                self._unknown_players.append(player)
            else:
                self._opponents.append(player)
        if self._our_side == SideID.RIGHT:
            self.reverse()

        for o in [self.ball()] + self._teammates + self._opponents + self._unknown_players:
            o.update_more_with_full_state(self)

    def update_just_before_decision(self, act: 'ActionEffector', current_time: GameTime):
        self._set_play_count += 1

        self.update_ball_by_hear(act)
        self.update_goalie_by_hear()
        self.update_players_by_hear()
        self.update_player_stamina_by_hear()
        # TODO UPDATE BALL BY COLLISION
        self.ball().update_by_game_mode(self.game_mode())
        self.ball().update_self_related(self.self(), self._prev_ball)
        self.self().update_ball_info(self.ball())
        self.update_player_state_cache()
        self.update_player_type()
        # TODO update player cards and player types
        # TODO update players collision
        self.update_their_defense_line()
        self.update_offside_line()
        # self.update_last_kicker() # TODO IMP FUNC
        self.update_intercept_table()

        # TODO update maybe kickable teammates
        self.self().update_kickable_state(self.ball(),
                                          self.intercept_table().self_reach_cycle(),
                                          self.intercept_table().teammate_reach_cycle(),
                                          self.intercept_table().opponent_reach_cycle())

        if DEBUG:
            log.sw_log().world().add_text('===After processing see message===')
            log.sw_log().world().add_text(f'===Our Players=== {len(self.our_players())} {self._name}')
            for p in self.our_players():
                log.sw_log().world().add_text(str(p))
            log.sw_log().world().add_text(f'===Their Players=== {len(self.their_players())} {self._name}')
            for p in self.their_players():
                log.sw_log().world().add_text(str(p))
            log.os_log().debug('===After processing see message===')
            # log.os_log().debug('===Ball===\n' + str(self.ball().long_str()))
            log.os_log().debug(f'===Our Players=== {len(self.our_players())} {self._name}')
            # log.os_log().debug('-----------------------')
            # for p in self.our_players():
            #     log.os_log().debug('-----------------------')
            #     log.os_log().debug(str(self.self()) if p.is_self() else str(p.long_str()))
            log.os_log().debug(f'===Their Players=== {len(self.their_players())} {self._name}')
            # for p in self.their_players():
            #     log.os_log().debug('-----------------------')
            #     log.os_log().debug(str(p.long_str()))

    def update_just_after_decision(self, act: 'ActionEffector'):
        self._decision_time = self.time().copy()
        if act.change_view_command():
            self.self().set_view_mode(act.change_view_command().width())
        if act.pointto_command():
            self.self().set_pointto(act.pointto_pos(),
                                    self.time())
        
        attention = act.attentionto_command()
        if attention:
            if attention.is_on():
                if attention.side() == PlayerAttentiontoCommand.SideType.OUR:
                    self.self().set_attentionto(self.our_side(), attention.number())
                else:
                    self.self().set_attentionto(self.their_side(), attention.number())
            else:
                self.self().set_attentionto(SideID.NEUTRAL, 0)

    
    def update_players_by_hear(self):
        # TODO FULLSTATTE MODE CHECK
        log.sw_log().world().add_text(f'{"#"*20} UPDATE PLAYER BY HEAR {"#"*20}')

        if self._messenger_memory.player_time() != self.time() or len(self._messenger_memory.players()) == 0:
            return
        
        for player in self._messenger_memory.players():

            if player.unum_ == UNUM_UNKNOWN:
                return
            
            side = self.our_side() if player.unum_ <= 11 else self.their_side()
            unum = player.unum_ if player.unum_ <= 11 else player.unum_ - 11
            unum = round(unum)

            if side == self.our_side() and unum == self.self().unum():
                return
            
            target_player: PlayerObject = None
            unknown: PlayerObject = None
            players = self._teammates if side == self.our_side() else self._opponents
            for p in players:
                if p.unum() == unum:
                    target_player = p
                    break
            
            min_dist = 1000
            if target_player is None:
                for p in players:
                    if p.unum() != UNUM_UNKNOWN and p.unum() != unum:
                        continue
                    
                    d = p.pos().dist(player.pos_)
                    if d < min_dist and p.pos_count()*1.2 + p.dist_from_self() *0.06:
                        min_dist = d
                        target_player = p
                
                for p in self._unknown_players:
                    d = p.pos().dist(player.pos_)
                    if d < min_dist and d < p.pos_count()*1.2 + p.dist_from_self() *0.06:
                        min_dist = d
                        target_player = p
                        unknown = p
            if target_player:
                target_player.update_by_hear(side, unum, False, player.pos_, player.body_)
                log.sw_log().world().add_text(f'(update player by hear) updating player '
                                                 f's={side} u={unum} p={player.pos_} b={player.body_}')

                if unknown:
                    players.append(unknown)
                    self._unknown_players.remove(unknown)
            
            else:
                target_player = PlayerObject()
                if side == self.our_side():
                    self._teammates.append(target_player)
                else:
                    
                    self._opponents.append(target_player)
                target_player.update_by_hear(side, unum, False, player.pos_, player.unum_)
                log.sw_log().world().add_text(f'(update player by hear) adding player '
                                                 f's={side} u={unum} p={player.pos_} b={player.body_}')

            if target_player:
                if side == self.our_side():
                    if 1 <= unum <= 11:
                        target_player.set_player_type(self._player_types[self._our_players_type[unum-1]])
                    else:
                        target_player.set_player_type(self._player_types[HETERO_DEFAULT])
                else:
                    if 1 <= unum <= 11:
                        target_player.set_player_type(self._player_types[self._their_players_type[unum-1]])
                    else:
                        target_player.set_player_type(self._player_types[HETERO_DEFAULT])
                
    
    def update_ball_by_hear(self, act: 'ActionEffector'):
        # TODO CHECK FULLSTATE MODE

        log.sw_log().world().add_text(f'{"#"*20} UPDATE BALL BY HEAR {"#"*20}')
        if self._messenger_memory.ball_time() != self.time() or len(self._messenger_memory.balls()) == 0:
            return
        
        heared_pos = Vector2D.invalid()
        heared_vel = Vector2D.invalid()

        min_dist = 1000
        for ball in self._messenger_memory.balls():

            sender: PlayerObject = None
            for player in self._teammates:
                if player.unum() == ball.sender_:
                    sender = player
                    break
            
            if sender:
                dist = sender.pos().dist(self.ball().pos())
                if dist < min_dist:
                    min_dist = dist
                    heared_pos = ball.pos_
                    
                    if ball.vel_.is_valid():
                        heared_vel = ball.vel_
            elif min_dist > 900:
                min_dist = 900
                heared_pos = ball.pos_
                if ball.vel_.is_valid():
                        heared_vel = ball.vel_

        if heared_pos.is_valid():
            self._ball.update_by_hear(act, min_dist, heared_pos, heared_vel)
            log.sw_log().world().add_text(f'(update ball by hear) '
                                             f'p={heared_pos} v={heared_vel}')

    def update_dir_count(self, varea: ViewArea):
        dir_buf = (WorldModel.DIR_STEP*0.5+1
                   if self.self().last_move().is_valid()
                   and self.self().last_move().r() > 0.5
                   else WorldModel.DIR_STEP * 0.5)

        left_limit = varea.angle() - varea.viewWidth() *0.5 + dir_buf
        right_limit = varea.angle() + varea.viewWidth() *0.5 - dir_buf
        
        left_dir = varea.angle() - varea.viewWidth() *0.5
        idx = int((left_dir.degree() - 0.5 + 180)/WorldModel.DIR_STEP)
        
        dir = AngleDeg(-180 + WorldModel.DIR_STEP*idx)
        while dir.is_left_of(left_limit):
            dir += WorldModel.DIR_STEP
            idx += 1
            if idx > WorldModel.DIR_CONF_DIVS:
                idx = 0
        
        
        while dir.is_left_of(right_limit):
            idx = int((dir.degree() - 0.5 + 180) / WorldModel.DIR_STEP)
            if idx > WorldModel.DIR_CONF_DIVS - 1:
                log.os_log().warn(f"{self.team_name()}({self.self().unum()}) DIR CONF overflow! idx={idx}")
                idx = WorldModel.DIR_CONF_DIVS - 1
            elif idx < 0:
                log.os_log().error(f"{self.team_name()}({self.self().unum()}) DIR CONF downflow! idx={idx}")
                idx = 0
            self._dir_count[idx] = 0
            dir += WorldModel.DIR_STEP
    
    def dir_count(self, angle: Union[AngleDeg, float]):
        angle = AngleDeg(angle).degree()
        
        idx = int((angle - 0.5 + 180) / WorldModel.DIR_STEP)
        if not 0 <= idx <= WorldModel.DIR_CONF_DIVS:
            log.os_log().error(f"(world model dir conf) index out of range! idx={idx}")
            idx = 0
        return self._dir_count[idx]
    
    def teammates(self):
        return self._teammates
    
    def opponents(self):
        return self._opponents

    def unknown_players(self):
        return self._unknown_players
    
    def all_players(self):
        return self._all_players

    def check_ghost(self, varea: ViewArea):
        SP = ServerParam.i()

        angle_buf = 5.
        
        if self.ball().rpos_count() > 0 and self.ball().pos_valid():
            ball_vis_dist2 = (
                SP.visible_distance()
                - (self.self().vel().r() / self.self().player_type().player_decay()) * 0.1
                - (self.ball().vel().r() / SP.ball_decay()) * 0.05
                - (0.12 * min(4, self.ball().pos_count()))
                - 0.25
            )**2
            
            if varea.contains(self.ball().pos(), angle_buf, ball_vis_dist2):
                self._ball.set_ghost()
        
        vis_dist2 = (
            SP.visible_distance()
            - (self.self().vel().r() / self.self().player_type().player_decay()) * 0.1
            - 0.25
            )**2
        
        removing_teammates = []
        for p in self._teammates:
            if p.pos_count() > 0 and varea.contains(p.pos(), angle_buf, vis_dist2):
                if p.unum() == UNUM_UNKNOWN and p.pos_count() >= 10 and p.ghost_count() >= 2:
                    removing_teammates.append(p)
                    continue
                p.set_ghost()
        for p in removing_teammates:
            self._teammates.remove(p)
        
        removing_opponents = []
        for p in self._opponents:
            if p.pos_count() > 0 and varea.contains(p.pos(), 1., vis_dist2):
                if p.unum() == UNUM_UNKNOWN and p.pos_count() >= 10 and p.ghost_count() >= 2:
                    removing_opponents.append(p)
                    continue
                log.sw_log().world().add_text(f'opponent is going to be a ghost: {p}')
                p.set_ghost()
        for p in removing_opponents:
            self._opponents.remove(p)
        
        removing_unknown_players = []
        for p in self._unknown_players:
            if p.pos_count() > 0 and varea.contains(p.pos(), 1., vis_dist2):
                if p.dist_from_self() < 40 *1.06 and p.is_ghost():
                    removing_unknown_players.append(p)
                    continue
                p.set_ghost()
        for p in removing_unknown_players:
            self._unknown_players.remove(p)

    def kickable_teammate(self):
        return self._kickable_teammate

    def kickable_opponent(self):
        return self._kickable_opponent

    def dir_range_count(self, angel: AngleDeg, width: float) -> tuple[int, int, int]:
        if not 0< width <= 360:
            return None

        counter = 0
        tmp_sum_count = 0
        tmp_max_count = 0

        tmp_angle = angel.copy()
        if width > WorldModel.DIR_STEP:
            tmp_angle -= width* 0.5

        add_dir = 0
        while add_dir < width:
            c = self.dir_count(tmp_angle)

            tmp_sum_count += c
            if c > tmp_max_count:
                tmp_max_count = c

            add_dir += WorldModel.DIR_STEP
            tmp_angle += WorldModel.DIR_STEP
            counter += 1

        return tmp_max_count, tmp_sum_count, int(tmp_sum_count/ counter)

    def messenger_memory(self):
        return self._messenger_memory
        
    def our_players(self):
        return self._our_players

    def their_players(self):
        return self._their_players

    def prev_ball(self):
        return self._prev_ball

    def get_their_goalie(self):
        if self._their_goalie_unum != UNUM_UNKNOWN:
            return self.their_player(self._their_goalie_unum)

        for p in self._opponents:
            if p.goalie():
                return p
        return None

    def set_our_player_type(self, unum: int, player_type_id: int):
        if not (1 <= unum <= 11):
            return

        log.sw_log().world().add_text(f'(ste ourplayer type) unum={unum}, type={player_type_id}')

        self._our_recovery[unum - 1] = 1.
        self._our_stamina_capacity[unum - 1] = ServerParam.i().stamina_capacity()

        self._our_players_type[unum - 1] = player_type_id
        self._our_card[unum - 1] = Card.NO_CARD

        if unum == self.self().unum():
            tmp = self._player_types[player_type_id]
            if tmp is None:
                log.os_log().error(f'{self.team_name()} {self.self().unum()}: illegal player type id')
                return
            self.self().set_player_type(tmp)

    def set_play_count(self):
        return self._set_play_count

    def exist_teammates_in(self, region: Region2D, count_thr: int, with_goalie: bool):
        for p in self._teammates:
            if p is None:
                continue
            if p.pos_count() > count_thr or p.is_ghost():
                continue
            if region.contains(p.pos()):
                return True
        return False
