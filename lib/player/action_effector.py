from typing import Union

from lib.debug.debug import log
from lib.debug.level import Level
from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.soccer_math import min_max
from pyrusgeom.vector_2d import Vector2D
from lib.messenger.messenger import Messenger
from lib.parser.parser_message_fullstate_world import FullStateWorldMessageParser
from lib.player.sensor.body_sensor import SenseBodyParser
from lib.player_command.player_command import CommandType
from lib.player_command.player_command_body import PlayerBodyCommand, PlayerCatchCommand, PlayerDashCommand, PlayerKickCommand, PlayerMoveCommand, PlayerTackleCommand, PlayerTurnCommand
from lib.player_command.player_command_support import PlayerAttentiontoCommand, PlayerChangeViewCommand, PlayerPointtoCommand, PlayerSayCommand, PlayerTurnNeckCommand, PlayerChangeFocusCommand
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType, SideID, ViewWidth

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel
    from lib.player.player_agent import PlayerAgent



class ActionEffector:
    def __init__(self, agent=None) -> None:
        self._agent: 'PlayerAgent' = agent

        self._body_command: PlayerBodyCommand = None
        self._neck_command: PlayerTurnNeckCommand = None
        self._pointto_command: PlayerPointtoCommand = None
        self._change_view_command: PlayerChangeViewCommand = None
        self._change_focus_command: PlayerChangeFocusCommand = None
        self._say_command: PlayerSayCommand = None
        self._attentionto_command: PlayerAttentiontoCommand = None

        self._command_counter: list[int] = [0 for _ in range(len(CommandType))]
        self._last_body_commands: list[CommandType] = [CommandType.ILLEGAL for _ in range(2)]
        self._last_action_time: GameTime = GameTime()

        self._kick_accel: Vector2D = Vector2D(0, 0)
        self._kick_accel_error: Vector2D = Vector2D(0, 0)

        self._turn_actual: float = 0
        self._turn_error: float = 0

        self._dash_accel: Vector2D = Vector2D(0, 0)
        self._dash_power: float = 0
        self._dash_dir: float = 0

        self._move_pos: Vector2D = Vector2D(0, 0)

        self._catch_time: GameTime = GameTime()

        self._tackle_power: float = 0
        self._tackle_dir: float = 0
        self._tackle_foul: bool = False

        self._turn_neck_moment: float = 0
        self._done_turn_neck: bool = False

        self._change_focus_moment_dist: float = 0
        self._change_focus_moment_dir: AngleDeg = AngleDeg(0)
        self._done_change_focus = False

        self._say_message: str = ''
        self._messages: list[Messenger] = []

        self._pointto_pos: Vector2D = Vector2D(0, 0)

    def change_view_command(self):
        return self._change_view_command

    def change_focus_point_command(self):
        return self._change_focus_command

    def pointto_command(self):
        return self._pointto_command

    def pointto_pos(self):
        return self._pointto_pos

    def attentionto_command(self):
        return self._attentionto_command

    def inc_command_type(self, type: CommandType):
        self._command_counter[type.value] += 1


    def check_command_count_with_fullstate_parser(self, full_sensor: FullStateWorldMessageParser): # TODO CALL it
        wm = self._agent.world()
        if full_sensor.kick_count() != self._command_counter[CommandType.KICK.value]:
            log.os_log().error(f"player({wm.self().unum()} lost kick at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()} lost kick at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()} lost kick at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._kick_accel = Vector2D(0, 0)
            self._kick_accel_error = Vector2D(0, 0)
            self._command_counter[CommandType.KICK.value] = full_sensor.kick_count()

        if full_sensor.turn_count() != self._command_counter[CommandType.TURN.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost TURN at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost TURN at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost TURN at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._turn_actual = 0
            self._turn_error = 0
            self._command_counter[CommandType.TURN.value] = full_sensor.turn_count()

        if full_sensor.dash_count() != self._command_counter[CommandType.DASH.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost DASH at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost DASH at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost DASH at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._dash_accel = Vector2D(0, 0)
            self._dash_power = 0
            self._dash_dir = 0
            self._command_counter[CommandType.DASH.value] = full_sensor.dash_count()

        if full_sensor.move_count() != self._command_counter[CommandType.MOVE.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost MOVE at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost MOVE at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost MOVE at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._move_pos = Vector2D(0, 0)
            self._command_counter[CommandType.MOVE.value] = full_sensor.move_count()
        if full_sensor.catch_count() != self._command_counter[CommandType.CATCH.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost CATCH at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost CATCH at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost CATCH at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            # self._catch_time = GameTime()
            self._command_counter[CommandType.CATCH.value] = full_sensor.catch_count()

        # if full_sensor.tackle_count() != self._command_counter[CommandType.TACKLE.value]:
        #     log.os_log().error(f"player({wm.self().unum()}) lost TACKLE at cycle {wm.time()}")
        #     log.sw_log().action().add_text(f"player({wm.self().unum()}) lost TACKLE at cycle {wm.time()}")
        #     log.debug_client().add_message(f"player({wm.self().unum()}) lost TACKLE at cycle {wm.time()}")
        #
        #     self._last_body_commands[0] = CommandType.ILLEGAL
        #     self._tackle_power = 0
        #     self._tackle_dir = 0
        #     self._tackle_foul = False
        #     self._command_counter[CommandType.TACKLE.value] = full_sensor.tackle_count()

        if full_sensor.turn_neck_count() != self._command_counter[CommandType.TURN_NECK.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost command TURN_NECK at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command TURN_NECK at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost command TURN_NECK at cycle {wm.time()}")
            self._command_counter[CommandType.TURN_NECK.value] = full_sensor.turn_neck_count()
            self._done_turn_neck = False
            self._turn_neck_moment = 0

        # if full_sensor.change_focus_count() != self._command_counter[CommandType.CHANGE_FOCUS.value]:
        #     log.os_log().error(f"player({wm.self().unum()}) lost command CHANGE_FOCUS at cycle {wm.time()}")
        #     log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command CHANGE_FOCUS at cycle {wm.time()}")
        #     log.debug_client().add_message(f"player({wm.self().unum()}) lost command CHANGE_FOCUS at cycle {wm.time()}")
        #     self._command_counter[CommandType.CHANGE_FOCUS.value] = body_sensor.change_focus_count()
        #     self._done_change_focus = False
        #     self._change_focus_moment_dist = 0
        #     self._change_focus_moment_dir = AngleDeg(0)

        if full_sensor.change_view_count() != self._command_counter[CommandType.CHANGE_VIEW.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost command CHANGE_VIEW at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command CHANGE_VIEW at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost command CHANGE_VIEW at cycle {wm.time()}")
            self._command_counter[CommandType.CHANGE_VIEW.value] =   full_sensor.change_view_count()

        if full_sensor.say_count() != self._command_counter[CommandType.SAY.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost command SAY at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command SAY at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost command SAY at cycle {wm.time()}")
            self._command_counter[CommandType.SAY.value]  = full_sensor.say_count()

        # if body_sensor.pointto_count() != self._command_counter[CommandType.POINTTO.value]:
        #     log.os_log().error(f"player({wm.self().unum()}) lost command POINTTO at cycle {wm.time()}")
        #     log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command POINTTO at cycle {wm.time()}")
        #     log.debug_client().add_message(f"player({wm.self().unum()}) lost command POINTTO at cycle {wm.time()}")
        #     self._command_counter[CommandType.POINTTO.value]  = full_sensor.pointto_count()

        # if full_sensor.attentionto_count() != self._command_counter[CommandType.ATTENTIONTO.value]:
        #     log.os_log().error(f"player({wm.self().unum()}) lost command ATTENTIONTO at cycle {wm.time()}")
        #     log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command ATTENTIONTO at cycle {wm.time()}")
        #     log.debug_client().add_message(f"player({wm.self().unum()}) lost command ATTENTIONTO at cycle {wm.time()}")
        #     self._command_counter[CommandType.ATTENTIONTO.value] =   full_sensor.attentionto_count()


    def check_command_count(self, body_sensor: SenseBodyParser):
        wm = self._agent.world()
        if body_sensor.kick_count() != self._command_counter[CommandType.KICK.value]:
            if body_sensor.charged_expires() == 0:
                log.os_log().error(f"player({wm.self().unum()} lost kick at cycle {wm.time()}")
                log.sw_log().action().add_text(f"player({wm.self().unum()} lost kick at cycle {wm.time()}")
                log.debug_client().add_message(f"player({wm.self().unum()} lost kick at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._kick_accel = Vector2D(0, 0)
            self._kick_accel_error = Vector2D(0, 0)
            self._command_counter[CommandType.KICK.value] = body_sensor.kick_count()

        if body_sensor.turn_count() != self._command_counter[CommandType.TURN.value]:
            if body_sensor.charged_expires() == 0:
                log.os_log().error(f"player({wm.self().unum()}) lost TURN at cycle {wm.time()}")
                log.sw_log().action().add_text(f"player({wm.self().unum()}) lost TURN at cycle {wm.time()}")
                log.debug_client().add_message(f"player({wm.self().unum()}) lost TURN at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._turn_actual = 0
            self._turn_error = 0
            self._command_counter[CommandType.TURN.value] = body_sensor.turn_count()

        if body_sensor.dash_count() != self._command_counter[CommandType.DASH.value]:
            if body_sensor.charged_expires() == 0:
                log.os_log().error(f"player({wm.self().unum()}) lost DASH at cycle {wm.time()}")
                log.sw_log().action().add_text(f"player({wm.self().unum()}) lost DASH at cycle {wm.time()}")
                log.debug_client().add_message(f"player({wm.self().unum()}) lost DASH at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._dash_accel = Vector2D(0, 0)
            self._dash_power = 0
            self._dash_dir = 0
            self._command_counter[CommandType.DASH.value] = body_sensor.dash_count()
        if body_sensor.move_count() != self._command_counter[CommandType.MOVE.value]:
            if body_sensor.charged_expires() == 0:
                log.os_log().error(f"player({wm.self().unum()}) lost MOVE at cycle {wm.time()}")
                log.sw_log().action().add_text(f"player({wm.self().unum()}) lost MOVE at cycle {wm.time()}")
                log.debug_client().add_message(f"player({wm.self().unum()}) lost MOVE at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._move_pos = Vector2D(0, 0)
            self._command_counter[CommandType.MOVE.value] = body_sensor.move_count()
        if body_sensor.catch_count() != self._command_counter[CommandType.CATCH.value]:
            if body_sensor.charged_expires() == 0:
                log.os_log().error(f"player({wm.self().unum()}) lost CATCH at cycle {wm.time()}")
                log.sw_log().action().add_text(f"player({wm.self().unum()}) lost CATCH at cycle {wm.time()}")
                log.debug_client().add_message(f"player({wm.self().unum()}) lost CATCH at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            # self._catch_time = GameTime()
            self._command_counter[CommandType.CATCH.value] = body_sensor.catch_count()
        if body_sensor.tackle_count() != self._command_counter[CommandType.TACKLE.value]:
            if body_sensor.charged_expires() == 0:
                log.os_log().error(f"player({wm.self().unum()}) lost TACKLE at cycle {wm.time()}")
                log.sw_log().action().add_text(f"player({wm.self().unum()}) lost TACKLE at cycle {wm.time()}")
                log.debug_client().add_message(f"player({wm.self().unum()}) lost TACKLE at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._tackle_power = 0
            self._tackle_dir = 0
            self._tackle_foul = False
            self._command_counter[CommandType.TACKLE.value] = body_sensor.tackle_count()

        if body_sensor.turn_neck_count() != self._command_counter[CommandType.TURN_NECK.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost command TURN_NECK at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command TURN_NECK at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost command TURN_NECK at cycle {wm.time()}")
            self._command_counter[CommandType.TURN_NECK.value] = body_sensor.turn_neck_count()
            self._done_turn_neck = False
            self._turn_neck_moment = 0

        if body_sensor.change_focus_count() != self._command_counter[CommandType.CHANGE_FOCUS.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost command CHANGE_FOCUS at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command CHANGE_FOCUS at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost command CHANGE_FOCUS at cycle {wm.time()}")
            self._command_counter[CommandType.CHANGE_FOCUS.value] = body_sensor.change_focus_count()
            self._done_change_focus = False
            self._change_focus_moment_dist = 0
            self._change_focus_moment_dir = AngleDeg(0)

        if body_sensor.change_view_count() != self._command_counter[CommandType.CHANGE_VIEW.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost command CHANGE_VIEW at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command CHANGE_VIEW at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost command CHANGE_VIEW at cycle {wm.time()}")
            self._command_counter[CommandType.CHANGE_VIEW.value] =   body_sensor.change_view_count()

        if body_sensor.say_count() != self._command_counter[CommandType.SAY.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost command SAY at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command SAY at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost command SAY at cycle {wm.time()}")
            self._command_counter[CommandType.SAY.value]  = body_sensor.say_count()

        if body_sensor.pointto_count() != self._command_counter[CommandType.POINTTO.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost command POINTTO at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command POINTTO at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost command POINTTO at cycle {wm.time()}")
            self._command_counter[CommandType.POINTTO.value]  = body_sensor.pointto_count()

        if body_sensor.attentionto_count() != self._command_counter[CommandType.ATTENTIONTO.value]:
            log.os_log().error(f"player({wm.self().unum()}) lost command ATTENTIONTO at cycle {wm.time()}")
            log.sw_log().action().add_text(f"player({wm.self().unum()}) lost command ATTENTIONTO at cycle {wm.time()}")
            log.debug_client().add_message(f"player({wm.self().unum()}) lost command ATTENTIONTO at cycle {wm.time()}")
            self._command_counter[CommandType.ATTENTIONTO.value] =   body_sensor.attentionto_count()

    @staticmethod
    def conserve_dash_power(wm: 'WorldModel', power, rel_dir):
        log.sw_log().action().add_text( f"(conserved dash power) power={power}")

        SP = ServerParam.i()
        required_stamina = power
        available_stamina = wm.self().stamina() + wm.self().player_type().extra_stamina()

        if available_stamina < required_stamina:
            log.sw_log().action().add_text( f"(conserve dash power) not enough stamina. power={power} stamina={available_stamina}")
            power = available_stamina

        dir_rate = SP.dash_dir_rate(rel_dir)
        accel_mag = abs(power*dir_rate*wm.self().dash_rate())
        accel_angle = wm.self().body() + rel_dir
        _, accel_mag = wm.self().player_type().normalize_accel(wm.self().vel(),
                                                accel_angle=accel_angle,
                                                accel_mag=accel_mag)

        power = accel_mag / wm.self().dash_rate() / dir_rate
        power = SP.normalize_dash_power(power)

        log.sw_log().action().add_text( f"(conserved dash power) conserved power={power}")

        return power

    def set_kick(self, power: float, rel_dir: Union[AngleDeg, float]):
        wm = self._agent.world()

        rel_dir = float(rel_dir)

        if power < ServerParam.i().min_power() or power > ServerParam.i().max_power():
            log.os_log().error(f"(set kick) player({wm.self().unum()}) power is out of boundary at cycle {wm.time()}. power={power}")
            power = ServerParam.i().max_power() if power > 100 else ServerParam.i().min_power()

        log.sw_log().action().add_text( f"(set kick) power={power}, rel_dir={rel_dir}")
        self._kick_accel = Vector2D.polar2vector(power * wm.self().kick_rate(),
                                                 wm.self().body() + rel_dir)
        max_rand = wm.self().player_type().kick_rand()*power/ServerParam.i().max_power()
        self._kick_accel_error = Vector2D(max_rand, max_rand)

        self._body_command = PlayerKickCommand(power, rel_dir)
        return self._body_command

    def set_dash(self, power: float, rel_dir: Union[AngleDeg, float] = 0):
        SP = ServerParam.i()
        wm = self._agent.world()

        rel_dir = float(rel_dir)

        if power > SP.max_dash_power() or power < SP.min_dash_power():
            log.os_log().error(f"(set dash) player({wm.self().unum()}) power is out of boundary at cycle {wm.time()}. power={power}")
            SP.normalize_dash_power(power)

        if rel_dir > SP.max_dash_angle() or rel_dir < SP.min_dash_angle():
            log.os_log().error(f"(set dash) player({wm.self().unum()}) rel_dir is out of boundary at cycle {wm.time()}. power={power}")
            SP.normalize_dash_angle(rel_dir)

        rel_dir = SP.discretize_dash_angle(rel_dir)

        power = ActionEffector.conserve_dash_power(wm, power, rel_dir)

        dir_rate = SP.dash_dir_rate(rel_dir)
        accel_mag = abs(power*dir_rate*wm.self().dash_rate())
        accel_mag = min(accel_mag, SP.player_accel_max())
        accel_angle = wm.self().body() + rel_dir

        self._dash_power = power
        self._dash_dir = rel_dir
        self._dash_accel = Vector2D.polar2vector(accel_mag, accel_angle)

        log.sw_log().action().add_text( f"(set dash) power={power}, rel_dir={rel_dir}, accel={self._dash_accel}")

        self._body_command = PlayerDashCommand(power, rel_dir)
        return self._body_command

    def set_turn(self, moment: Union[AngleDeg, float]):
        moment = float(AngleDeg(moment))
        SP = ServerParam.i()
        wm = self._agent.world()
        speed = wm.self().vel().r()

        moment *= 1 + speed * wm.self().player_type().inertia_moment()
        if moment > SP.max_moment() or moment < SP.min_moment():
            log.os_log().error(f"(set turn) player({wm.self().unum()}) moment is out of boundary at cycle {wm.time()}. moment={moment}")
            moment = SP.max_moment() if moment > SP.max_moment() else SP.min_moment()

        self._turn_actual = moment / (1 + speed*wm.self().player_type().inertia_moment())
        self._turn_error = abs(SP.player_rand()*self._turn_actual)

        log.sw_log().action().add_text( f"(set turn) moment={moment}, actual_turn={self._turn_actual}, error={self._turn_error}")
        log.os_log().debug(f"(set turn) moment={moment}, actual_turn={self._turn_actual}, error={self._turn_error}")

        self._body_command = PlayerTurnCommand(round(moment, 2))
        return self._body_command

    def set_move(self, x: float, y: float):
        SP = ServerParam.i()
        wm = self._agent.world()

        if abs(x) > SP.pitch_half_length() or abs(y) > SP.pitch_half_width():
            log.os_log().error(f"(set move) player({wm.self().unum()}) position is out of pitch at cycle {wm.time()}. pos=({x},{y})")
            x = min_max(-SP.pitch_half_length(), x, SP.pitch_half_length())
            y = min_max(-SP.pitch_half_width(), y, SP.pitch_half_width())

        if SP.kickoff_offside() and x > 0:
            log.os_log().error(f"(set move) player({wm.self().unum()}) position is in opponent side at cycle {wm.time()}. pos=({x},{y})")
            x = -0.1

        if wm.game_mode().type().is_goalie_catch_ball() and wm.game_mode().side() == wm.our_side():
            if x < -SP.pitch_half_length() + 1 or x > -SP.our_penalty_area_line_x() - 1:
                log.os_log().error(f"(set move) player({wm.self().unum()}) position is out of penalty area at cycle {wm.time()}. pos=({x},{y})")
                x = min_max(-SP.pitch_half_length()+1, x, -SP.our_penalty_area_line_x()-1)
            if abs(y) > SP.penalty_area_half_width() -1:
                log.os_log().error(f"(set move) player({wm.self().unum()}) position is out of penalty area at cycle {wm.time()}. pos=({x},{y})")
                y = min_max(-SP.penalty_area_half_width(),y, SP.penalty_area_half_width())

        self._move_pos.assign(x, y)

        self._body_command = PlayerMoveCommand(x, y)
        return self._body_command

    def set_catch(self):
        SP = ServerParam.i()
        wm = self._agent.world()

        diagonal_angle = AngleDeg.atan2_deg(SP.catch_area_w()*0.5, SP.catch_area_l())
        ball_rel_angle = wm.ball().angle_from_self() - wm.self().body()
        catch_angle = (ball_rel_angle + diagonal_angle).degree()

        if not (SP.min_catch_angle() < catch_angle < SP.max_catch_angle()):
            catch_angle = ball_rel_angle - diagonal_angle

        self._body_command = PlayerCatchCommand(catch_angle)
        return self._body_command

    def set_tackle(self, dir: Union[float, AngleDeg], foul: bool):
        wm = self._agent.world()

        dir = float(dir)
        if abs(dir) > 180:
            log.os_log().error(f"(set tackle) player({wm.self().unum()}) dir is out of range at cycle {wm.time()}. dir={dir}")
            dir = AngleDeg.normalize_angle(dir)

        self._tackle_power = ServerParam.i().max_tackle_power()
        self._tackle_dir = dir
        self._tackle_foul = foul

        self._body_command = PlayerTackleCommand(dir, foul)
        return self._body_command

    def set_turn_neck(self, moment: Union[AngleDeg, float]):
        SP = ServerParam.i()
        wm = self._agent.world()

        moment = float(moment)
        if not (SP.min_neck_moment() < moment < SP.max_neck_moment()):
            log.os_log().error(f"(set turn neck) player({wm.self().unum()}) moment is out of range at cycle {wm.time()}. moment={moment}")
            moment = min_max(SP.min_neck_moment(), moment, SP.max_neck_moment())

        next_neck_angle = wm.self().neck().degree() + moment
        if not(SP.min_neck_angle() < next_neck_angle < SP.max_neck_angle()):
            log.os_log().error(f"(set turn neck) player({wm.self().unum()}) \
                next neck angle is out of range at cycle {wm.time()}. next neck angle={next_neck_angle}")
            moment = min_max(SP.min_neck_angle(), next_neck_angle, SP.max_neck_angle()) - wm.self().neck().degree()
        self._turn_neck_moment = moment

        self._neck_command = PlayerTurnNeckCommand(round(moment, 2))
        return self._neck_command

    def set_change_focus(self, moment_dist: float, moment_dir: AngleDeg):
        self._change_focus_command = PlayerChangeFocusCommand(moment_dist, moment_dir)
        self._change_focus_moment_dist = moment_dist
        self._change_focus_moment_dir = moment_dir
        return self._change_focus_command

    def set_change_view(self, width: ViewWidth):
        self._change_view_command = PlayerChangeViewCommand(width)
        return self._change_view_command

    def set_pointto(self, x, y):
        wm = self._agent.world()

        target = Vector2D(x,y)
        target = target - wm.self().pos()
        target.rotate(-wm.self().face())

        self._pointto_command = PlayerPointtoCommand(target.r(), target.th())
        return self._pointto_command

    def set_pointto_off(self):
        self._pointto_command = PlayerPointtoCommand()
        return self._pointto_command

    def last_body_command(self, index: int = 0):
        return self._last_body_commands[min_max(0, index, 1)]

    def get_kick_info(self) -> Vector2D:
        return self._kick_accel

    def get_dash_info(self) -> tuple[Vector2D, float]:
        return self._dash_accel, self._dash_power

    def get_turn_info(self) -> float:
        return self._turn_actual

    def tackle_foul(self) -> bool:
        return self._tackle_foul

    def get_move_pos(self) -> Vector2D:
        return self._move_pos

    def get_turn_neck_moment(self) -> float:
        return self._turn_neck_moment

    def done_turn_neck(self) -> bool:
        return self._done_turn_neck

    def get_change_focus_moment_dist(self) -> float:
        return self._change_focus_moment_dist

    def get_change_focus_moment_dir(self) -> AngleDeg:
        return self._change_focus_moment_dir

    def done_change_focus(self) -> bool:
        return self._done_change_focus

    def reset(self):
        for i in range(len(self._last_body_commands)):
            self._last_body_commands[i] = None

        self._done_turn_neck = False
        self._done_change_focus = False
        self._say_message = ""

    def update_after_actions(self):
        self._last_body_commands[1] = self._last_body_commands[0]
        self._last_action_time = self._agent.world().time().copy()

        if self._body_command:
            self._last_body_commands[0] = self._body_command.type()
            if self._last_body_commands[0] is CommandType.CATCH:
                self._catch_time = self._agent.world().time().copy()

            self.inc_command_type(self._body_command.type())
            self._body_command = None

        if self._neck_command:
            self._done_turn_neck = True
            self.inc_command_type(CommandType.TURN_NECK)
            self._neck_command = None

        if self._change_view_command:
            self.inc_command_type(CommandType.CHANGE_VIEW)
            self._change_view_command = None

        if self._change_focus_command:
            self._done_change_focus = True
            self.inc_command_type(CommandType.CHANGE_FOCUS)
            self._change_focus_command = None

        if self._pointto_command:
            self.inc_command_type(CommandType.POINTTO)
            self._pointto_command = None

        if self._say_command:
            self.inc_command_type(CommandType.SAY)
            self._say_command = None

        if self._attentionto_command:
            self.inc_command_type(CommandType.ATTENTIONTO)
            self._attentionto_command = None

    def clear_all_commands(self):
        self._body_command = None
        self._neck_command = None
        self._change_view_command = None
        self._change_focus_command = None
        self._pointto_command = None
        self._attentionto_command = None
        self._say_command = None
        self._messages.clear()

    def add_say_message(self, message: Messenger):
        if message:
            self._messages.append(message)

    def make_say_message_command(self, wm: 'WorldModel'):
        if len(self._messages) == 0:
            return None

        say_command =  PlayerSayCommand(Messenger.encode_all(self._messages))
        if len(say_command.message()) == 0:
            return None

        return say_command

    def set_attentionto(self, side: SideID, unum: int):
        SIDE = PlayerAttentiontoCommand.SideType
        new_side = SIDE.NONE
        if side == self._agent.world().our_side():
            new_side = SIDE.OUR
        elif side == self._agent.world().their_side():
            new_side = SIDE.OPP
        else:
            new_side = SIDE.NONE
        self._attentionto_command = PlayerAttentiontoCommand(new_side, unum)
        return self._attentionto_command

    def set_attentionto_off(self):
        self._attentionto_command = PlayerAttentiontoCommand()
        return self._attentionto_command

    def queued_next_self_body(self) -> AngleDeg:
        next_angle = self._agent.world().self().body().copy()
        if self._body_command and self._body_command.type() is CommandType.TURN:
            moment = self.get_turn_info()
            next_angle += moment
        return next_angle

    def queued_next_view_width(self) -> ViewWidth:
        if self._change_view_command:
            return self._change_view_command.width()
        return self._agent.world().self().view_width()

    def queued_next_self_face(self) -> AngleDeg:
        next_face = self.queued_next_self_neck() + self.queued_next_self_body()
        return next_face

    def queued_next_self_neck(self):
        next_neck = self._agent.world().self().neck() + AngleDeg(self._turn_neck_moment)
        return next_neck

    def queued_next_focus_point(self) -> Vector2D:
        me = self._agent.world().self()
        next_focus_dist = me.focus_point_dist() + self.get_change_focus_moment_dist()
        next_focus_dir = me.focus_point_dir() + self.get_change_focus_moment_dir()
        next_view_width_half = self.queued_next_view_width().width() / 2.0
        next_focus_dir = min_max(-next_view_width_half, next_focus_dir.degree(), next_view_width_half)
        next_focus_dir_to_pos = self.queued_next_self_face() + next_focus_dir
        return self.queued_next_self_pos() + Vector2D.polar2vector(next_focus_dist, next_focus_dir_to_pos)

    def queued_next_self_pos(self) -> Vector2D:
        me = self._agent.world().self()
        vel = me.vel()
        if self._body_command and self._body_command.type() is CommandType.DASH:
            accel, _ = self.get_dash_info()
            vel += accel

            tmp = vel.r()
            if tmp > me.player_type().player_speed_max():
                vel *= me.player_type().player_speed_max() / tmp
        return me.pos() + vel

    def queued_next_ball_pos(self):
        wm = self._agent.world()

        if not wm.ball().pos_valid():
            return Vector2D.invalid()

        vel = Vector2D(0,0)
        accel = Vector2D(0,0)

        if wm.ball().vel_valid():
            vel = wm.ball().vel()

        if self._body_command and self._body_command.type() == CommandType.KICK:
            accel = self.get_kick_info()

        vel += accel
        return wm.ball().pos() + vel

    def queued_next_angle_from_body(self, target: Vector2D):
        next_rpos = target - self.queued_next_self_pos()
        return next_rpos.th() - self.queued_next_self_body()

    def queued_next_ball_vel(self):
        vel = Vector2D(0, 0)
        accel = Vector2D(0, 0)

        wm = self._agent.world()

        if wm.ball().vel_valid():
            vel = wm.ball().vel().copy()

        if self._body_command and self._body_command.type() == CommandType.KICK:
            accel = self.get_kick_info()

        vel += accel
        vel *= ServerParam.i().ball_decay()
        return vel

    def queued_next_ball_kickable(self):
        if self._agent.world().ball().rpos_count() >= 3:
            return False

        my_next = self.queued_next_self_pos()
        ball_next = self.queued_next_ball_pos()

        return my_next.dist(ball_next) < self._agent.world().self().player_type().kickable_area() - 0.06

    def get_say_message_length(self):
        l = 0
        for m in self._messages:
            l += m.size()
        return l

    def catch_time(self):
        return self._catch_time












