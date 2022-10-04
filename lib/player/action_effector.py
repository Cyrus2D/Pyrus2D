from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.angle_deg import AngleDeg
from lib.math.vector_2d import Vector2D
from lib.player.sensor.body_sensor import BodySensor
from lib.player_command.player_command import CommandType
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam


class ActionEffector:
    def __init__(self, agent) -> None:
        from lib.player.player_agent import PlayerAgent

        self._agent: PlayerAgent = agent

        self._command_counter: list[int] = [0 for _ in range(len(CommandType))]
        self._last_body_commands: list[int] = [
            CommandType.ILLEGAL for _ in range(2)]
        self._last_action_time: GameTime = GameTime()

        self._kick_accel: float = 0
        self._kick_accel_error: float = 0

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

        # self._say_message: str = ''

        self._pointto_pos: Vector2D = Vector2D(0, 0)

    def inc_command_type(self, type: CommandType):
        self._command_counter[type.value] += 1

    def check_command_count(self, body: BodySensor):
        wm = self._agent.world()
        if body.kick_count() == self._command_counter[CommandType.KICK]:
            if body.charged_expires() == 0:
                print(
                    f"player({wm.self().unum()} lost kick at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._kick_accel = 0
            self._kick_accel_error = 0
            self._command_counter[CommandType.KICK] = body.kick_count()

        if body.turn_count() == self._command_counter[CommandType.TURN]:
            if body.charged_expires() == 0:
                print(
                    f"player({wm.self().unum()}) lost TURN at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._turn_actual = 0
            self._turn_error = 0
            self._command_counter[CommandType.TURN] = body.turn_count()

        if body.dash_count() == self._command_counter[CommandType.DASH]:
            if body.charged_expires() == 0:
                print(
                    f"player({wm.self().unum()}) lost DASH at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._dash_accel = Vector2D(0, 0)
            self._dash_power = 0
            self._dash_dir = 0
            self._command_counter[CommandType.DASH] = body.dash_count()
        if body.move_count() == self._command_counter[CommandType.MOVE]:
            if body.charged_expires() == 0:
                print(
                    f"player({wm.self().unum()}) lost MOVE at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._move_pos = Vector2D(0, 0)
            self._command_counter[CommandType.MOVE] = body.move_count()
        if body.catch_count() == self._command_counter[CommandType.CATCH]:
            if body.charged_expires() == 0:
                print(
                    f"player({wm.self().unum()}) lost CATCH at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            # self._catch_time = GameTime()
            self._command_counter[CommandType.CATCH] = body.catch_count()
        if body.tackle_count() == self._command_counter[CommandType.TACKLE]:
            if body.charged_expires() == 0:
                print(
                    f"player({wm.self().unum()}) lost TACKLE at cycle {wm.time()}")

            self._last_body_commands[0] = CommandType.ILLEGAL
            self._tackle_power = 0
            self._tackle_dir = 0
            self._tackle_foul = False
            self._command_counter[CommandType.TACKLE] = body.tackle_count()
        
        if body.turn_neck_count() == self._command_counter[CommandType.TURN_NECK]:
            print(f"player({wm.self().unum()}) lost command TURN_NECK at cycle {wm.time()}")
            self._command_counter[CommandType.TURN_NECK] =   body.turn_neck_count()
            self._done_turn_neck = False
            self._turn_neck_moment = 0

        if body.change_view_count() == self._command_counter[CommandType.CHANGE_VIEW]:
            print(f"player({wm.self().unum()}) lost command CHANGE_VIEW at cycle {wm.time()}")
            self._command_counter[CommandType.CHANGE_VIEW] =   body.change_view_count()

        if body.say_count() == self._command_counter[CommandType.SAY]:
            print(f"player({wm.self().unum()}) lost command SAY at cycle {wm.time()}")
            self._command_counter[CommandType.SAY]  = body.say_count()

        if body.pointto_count() == self._command_counter[CommandType.POINTTO]:
            print(f"player({wm.self().unum()}) lost command POINTTO at cycle {wm.time()}")
            self._command_counter[CommandType.POINTTO]  = body.pointto_count()

        if body.attentionto_count() == self._command_counter[CommandType.ATTENTIONTO]:
            print(f"player({wm.self().unum()}) lost command ATTENTIONTO at cycle {wm.time()}")
            self._command_counter[CommandType.ATTENTIONTO] =   body.attentionto_count()
    
    @staticmethod
    def conserve_dash_power(wm, power, rel_dir):
        dlog.add_text(Level.ACTION, f"(conserved dash power) power={power}")

        SP = ServerParam.i()
        required_stamina = power
        available_stamina = wm.self().stamina() + wm.self().player_type().extra_stamina()
        
        if available_stamina < required_stamina:
            dlog.add_text(Level.ACTION, f"(conserve dash power) not enough stamina. power={power} stamina={available_stamina}")
            power = available_stamina
        
        dir_rate = SP.dash_dir_rate(rel_dir)
        accel_mag = abs(power*dir_rate*wm.self().dash_rate())
        accel_angle = wm.self().body() + rel_dir
        _, accel_mag = wm.self().player_type().normalize_accel(wm.self().vel(),
                                                accel_angle=accel_angle,
                                                accel_mag=accel_mag)
        
        power = accel_mag / wm.self().dashRate() / dir_rate
        power = SP.normalize_dash_power(power)
        
        dlog.add_text(Level.ACTION, f"(conserved dash power) conserved power={power}")
        
    def set_kick(self, power: float, rel_dir: AngleDeg | float):
        wm = self._agent.world()

        rel_dir = float(rel_dir)
        
        if power < 0 or power > 100:
            print(f"(set kick) player({wm.self().unum()}) power is out of boundary at cycle {wm.time()}. power={power}")
            power = ServerParam.i().max_power() if power > 100 else ServerParam.i().min_power()
        
        dlog.add_text(Level.ACTION, f"(set kick) power={power}, rel_dir={rel_dir}")
        self._kick_accel = Vector2D.polar2vector(power * wm.self().kick_rate(),
                                                 wm.self().body() + rel_dir)
        max_rand = wm.self().player_type().kick_rand()*power/ServerParam.i().max_power()
        self._kick_accel_error = Vector2D(max_rand, max_rand)
        
    def set_dash(self, power: float, rel_dir: AngleDeg | float = 0):
        SP = ServerParam.i()
        wm = self._agent.world()

        rel_dir = float(rel_dir)
        
        if power > 100 or power < 0:
            print(f"(set dash) player({wm.self().unum()}) power is out of boundary at cycle {wm.time()}. power={power}")
            SP.normalize_dash_power(power)
        
        if rel_dir > 100 or rel_dir < 0:
            print(f"(set dash) player({wm.self().unum()}) rel_dir is out of boundary at cycle {wm.time()}. power={power}")
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
        
        dlog.add_text(Level.ACTION, f"(set dash) power={power}, rel_dir={rel_dir}, accel={self._dash_accel}")


        
        
            


