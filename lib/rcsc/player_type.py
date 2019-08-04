from lib.parser.parser_message_params import MessageParamsParser
from lib.rcsc.server_param import ServerParam as SP
import lib.math.soccer_math as smath
from lib.math.geom_2d import *


class PlayerType:
    def __init__(self):
        self._id = 0
        self._player_speed_max = 1.05
        self._stamina_inc_max = 45
        self._player_decay = 0.4
        self._inertia_moment = 5
        self._dash_power_rate = 0.006
        self._player_size = 0.3
        self._kickable_margin = 0.7
        self._kick_rand = 0.1
        self._extra_stamina = 50
        self._effort_max = 1
        self._effort_min = 0.6
        self._kick_power_rate = 0.027
        self._foul_detect_probability = 0.5
        self._catchable_area_l_stretch = 1

        # update in init_additional_params
        self._kickable_area = 1.0
        self._reliable_catchable_dist = 1.0
        self._max_catchable_dist = 1.0
        self._real_speed_max = 1.0
        self._cycles_to_reach_max_speed = -1

        self._dash_distance_table = []
        self.init_additional_params()

    def set_data(self, dic):
        self._id = int(dic["id"])
        self._player_speed_max = float(dic["player_speed_max"])
        self._stamina_inc_max = float(dic["stamina_inc_max"])
        self._player_decay = float(dic["player_decay"])
        self._inertia_moment = float(dic["inertia_moment"])
        self._dash_power_rate = float(dic["dash_power_rate"])
        self._player_size = float(dic["player_size"])
        self._kickable_margin = float(dic["kickable_margin"])
        self._kick_rand = float(dic["kick_rand"])
        self._extra_stamina = float(dic["extra_stamina"])
        self._effort_max = float(dic["effort_max"])
        self._effort_min = float(dic["effort_min"])
        self._kick_power_rate = float(dic["kick_power_rate"])
        self._foul_detect_probability = float(dic["foul_detect_probability"])
        self._catchable_area_l_stretch = float(dic["catchable_area_l_stretch"])
        self.init_additional_params()

    def __repr__(self):
        return f"kickable_margin: {self.kickable_margin()}"

    def parse(self, message):
        parser = MessageParamsParser()
        parser.parse(message)
        self.set_data(parser.dic()['player_type'])

    def id(self):
        return self._id

    def player_speed_max(self):
        return self._player_speed_max

    def player_speed_max2(self):
        return self._player_speed_max ** 2

    def stamina_inc_max(self):
        return self._stamina_inc_max

    def player_decay(self):
        return self._player_decay

    def inertia_moment(self):
        return self._inertia_moment

    def dash_power_rate(self):
        return self._dash_power_rate

    def player_size(self):
        return self._player_size

    def kickable_margin(self):
        return self._kickable_margin

    def kick_rand(self):
        return self._kick_rand

    def extra_stamina(self):
        return self._extra_stamina

    def effort_max(self):
        return self._effort_max

    def effort_min(self):
        return self._effort_min

    def kick_power_rate(self):
        return self._kick_power_rate

    def foul_detect_probability(self):
        return self._foul_detect_probability

    def catchable_area_l_stretch(self):
        return self._catchable_area_l_stretch

    def kickable_area(self):
        return self._kickable_area

    def reliable_catchable_dist(self):
        return self._real_speed_max

    def max_catchable_dist(self):
        return self._max_catchable_dist

    def catchable_area(self):
        return self._max_catchable_dist

    def real_speed_max(self):
        return self._real_speed_max

    def init_additional_params(self):
        self._kickable_area = self.player_size() + self.kickable_margin() + SP.i().ball_size()  # TODO in cpp base define this in SP?!?!?!
        catch_stretch_length_x = (self.catchable_area_l_stretch() - 1.0) * SP.i().catch_area_l()
        catch_length_min_x = SP.i().catch_area_l() - catch_stretch_length_x
        catch_length_max_x = SP.i().catch_area_l() + catch_stretch_length_x
        catch_half_width2 = math.pow(SP.i().catch_area_w() / 2.0, 2)
        self._reliable_catchable_dist = math.sqrt(math.pow(catch_length_min_x, 2) + catch_half_width2)
        self._max_catchable_dist = math.sqrt(
            math.pow(catch_length_max_x, 2) + catch_half_width2)  # TODO catch_length_max_x { / 2} ?!
        accel = SP.i().max_dash_power() * self.dash_power_rate() * self.effort_max()
        self._real_speed_max = accel / (1.0 - self.player_decay())

        if self._real_speed_max > self.player_speed_max():
            self._real_speed_max = self.player_speed_max()

        speed = 0.0
        dash_power = SP.i().max_dash_power()
        reach_dist = 0.0

        self._dash_distance_table.clear()
        self._dash_distance_table = [0 for i in range(50)]
        for c in range(50):
            if speed + accel > self.player_speed_max():
                accel = self.player_speed_max() - speed
                dash_power = min(SP.i().max_dash_power(), accel / (self.dash_power_rate() * 1.0))  # should change
            speed += accel
            reach_dist += speed
            self._dash_distance_table[c] = reach_dist
            if self._cycles_to_reach_max_speed < 0 and speed >= self.real_speed_max() - 0.01:
                self._cycles_to_reach_max_speed = c
            # stamina_model.simulateDash(*this, dash_power);
            #
            # if (stamina_model.stamina() <= 0.0)
            #     {
            # break;
            # }
            #
            speed *= self.player_decay()

    def cycles_to_reach_max_speed(self, dash_power):
        accel = math.fabs(dash_power) * self.dash_power_rate() * self.effort_max()
        speed_max = accel / (1.0 - self.player_decay())
        if speed_max > self.player_speed_max():
            speed_max = self.player_speed_max()
        decn = 1.0 - ((speed_max - 0.01) * (1.0 - self.player_decay()) / accel)
        return int(math.ceil(math.log(decn) / math.log(self.player_decay())))

    def cycles_to_reach_distance(self, dash_dist):
        if dash_dist <= 0.001:
            return 0

        ddc = 0
        for dd in self._dash_distance_table:
            if dash_dist <= dd:
                return ddc
            ddc += 1

        cycle = len(self._dash_distance_table)
        rest_dist = dash_dist - self._dash_distance_table[cycle - 1]
        cycle += int(math.ceil(rest_dist / self.real_speed_max()))
        return cycle

    def kick_rate(self, ball_dist, dir_diff):
        return (self.kick_power_rate() * (1.0 - 0.25 * math.fabs(dir_diff) / 180.0 - (
                0.25 * (ball_dist - SP.i().ball_size() - self.player_size()) / self.kickable_margin())))

    def dash_rate(self, effort):  # , rel_dir):
        return effort * self.dash_power_rate()
        # return self.dash_rate(effort) * SP.i().dash_dir_rate(rel_dir)  # TODO bug :|

    def effective_turn(self, command_moment, speed):
        return command_moment / (1.0 + self.inertia_moment() * speed)

    def final_speed(self, dash_power, effort):
        return min(self.player_speed_max(),
                   ((math.fabs(dash_power) * self.dash_power_rate() * effort) / (1.0 - self.player_decay())))

    def inertia_travel(self, initial_vel, n_step):
        return smath.inertia_n_step_travel(initial_vel, n_step, self.player_decay())

    def inertia_point(self, initial_pos: Vector2D, initial_vel: Vector2D, n_step):
        return smath.inertia_n_step_point(initial_pos, initial_vel, n_step, self.player_decay())

    def inertia_final_travel(self, initial_vel: Vector2D):
        return smath.inertia_final_travel(initial_vel, self.player_decay())

    def inertiaFinalPoint(self, initial_pos: Vector2D, initial_vel: Vector2D):
        return smath.inertia_final_point(initial_pos, initial_vel, self.player_decay())

    def normalize_accel(self, vel: Vector2D, accel: Vector2D):
        if (vel + accel).r2() > self.player_speed_max2() + 0.0001:
            rel_vel = vel.rotated_vector(-accel.th())
            max_dash_x = (self.player_speed_max2() - rel_vel.y() - rel_vel.x()) ** 0.5
            accel.set_length(max_dash_x - rel_vel.x())
            return True
        return False

    def can_over_speed_max(self, dash_power: float, effort: float):
        return (abs(dash_power) * self.dash_power_rate() * effort
                > self.player_speed_max() * (1 - self.player_decay()))
