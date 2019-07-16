from lib.parser.parser_message_params import MessageParamsParser


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

