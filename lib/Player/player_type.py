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

    def parse(self, message):
        pass
