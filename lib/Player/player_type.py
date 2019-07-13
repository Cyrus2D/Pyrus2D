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
        self._id = dic["id"]
        self._player_speed_max = dic["player_speed_max"]
        self._stamina_inc_max = dic["stamina_inc_max"]
        self._player_decay = dic["player_decay"]
        self._inertia_moment = dic["inertia_moment"]
        self._dash_power_rate = dic["dash_power_rate"]
        self._player_size = dic["player_size"]
        self._kickable_margin = dic["kickable_margin"]
        self._kick_rand = dic["kick_rand"]
        self._extra_stamina = dic["extra_stamina"]
        self._effort_max = dic["effort_max"]
        self._effort_min = dic["effort_min"]
        self._kick_power_rate = dic["kick_power_rate"]
        self._foul_detect_probability = dic["foul_detect_probability"]
        self._catchable_area_l_stretch = dic["catchable_area_l_stretch"]

    def parse(self, message):
        dic = MessageParamsParser().parse(message)
        self.set_data(dic)
