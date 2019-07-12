class PlayerType:  # TODO spicfic TYPES and change them
    def __init__(self, dic):
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
