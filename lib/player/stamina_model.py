import copy
from lib.rcsc.game_time import GameTime

from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam


class StaminaModel:
    def __init__(self, stamina=None, effort=None, recovery=None, capacity=None):
        SP = ServerParam.i()
        self._stamina: float = float(stamina) if stamina else SP.stamina_max()
        self._effort: float = float(effort) if effort else SP.default_effort_max()
        self._recovery: float = float(recovery) if recovery else SP.recover_init()
        self._capacity: float = float(capacity) if capacity else -1

    def init(self, player_type: PlayerType):
        SP = ServerParam.i()
        self._stamina = SP.stamina_max()
        self._effort = player_type.effort_max()
        self._recovery = SP.recover_init()
        self._capacity = SP.stamina_capacity()

    def simulate_wait(self, player_type: PlayerType):
        SP = ServerParam.i()

        # recovery
        if self._stamina <= SP.recover_dec_thr_value():
            if self._recovery > SP.recover_min():
                self._recovery -= SP.recover_dec()
                self._recovery = max(self._recovery, SP.recover_min())

        # effort
        if self._stamina <= SP.effort_dec_thr_value():
            if self._effort > player_type.effort_min():
                self._effort -= SP.effort_dec()
                self._effort = max(self._effort, player_type.effort_min())
        elif self._stamina >= SP.effort_inc_thr_value():
            if self._effort < player_type.effort_max():
                self._effort += SP.effort_inc()
                self._effort = min(self._effort, player_type.effort_max())

        stamina_inc = min(player_type.stamina_inc_max() * self._recovery,
                          SP.stamina_max() - self._stamina)
        if SP.stamina_capacity() >= 0:
            self._stamina += min(stamina_inc, self._capacity)
            self._capacity -= stamina_inc
            self._capacity = max(0, self._capacity)
        else:
            self._stamina += stamina_inc
        self._stamina = min(self._stamina, SP.stamina_max()) 

    def simulate_waits(self, player_type: PlayerType, n_wait: int):
        for i in range(n_wait):
            self.simulate_wait(player_type)

    def capacity_is_empty(self) -> bool:
        return 0 <= self._capacity <= 1e-5

    def simulate_dash(self, player_type: PlayerType, dash_power: float):
        self._stamina -= dash_power if dash_power >= 0 else dash_power * -2
        self._stamina = max(0, self._stamina)
        self.simulate_wait(player_type)

    def simulate_dashes(self,
                        player_type: PlayerType,
                        n_dash: int,
                        dash_power: float):
        consumption = dash_power if dash_power >= 0 else dash_power * -2

        for i in range(n_dash):
            self._stamina -= consumption
            self._stamina = max(0, self._stamina)

            self.simulate_wait(player_type)

    def copy(self):
        return StaminaModel(self._stamina,
                            self._effort,
                            self._recovery,
                            self._capacity)

    def stamina(self):
        return self._stamina

    def effort(self):
        return self._effort

    def recovery(self):
        return self._recovery

    def capacity(self):
        return self._capacity

    def get_safety_dash_power(self, player_type: PlayerType, dash_power):
        normalized_power = ServerParam.i().normalize_dash_power(dash_power)
        required_stamina = (normalized_power
                            if normalized_power > 0
                            else normalized_power * -2)

        threshold = (-player_type.extra_stamina()
                     if self.capacity_is_empty()
                     else ServerParam.i().recover_dec_thr_value() + 1)
        safety_stamina = self._stamina - threshold
        available_stamina = max(0, safety_stamina)
        result_power = min(required_stamina, available_stamina)
        if normalized_power < 0:
            result_power *= -0.5
        if abs(result_power) > abs(normalized_power):
            return normalized_power

        return result_power

    def update_by_sense_body(self,
                             sensed_stamina: float,
                             sensed_effort: float,
                             sensed_capacity: float,
                             current_time: GameTime):
        SP = ServerParam.i()
        
        self._stamina = sensed_stamina
        self._effort = sensed_effort
        self._capacity = sensed_capacity

        half_time = SP.actual_half_time()
        normal_time = half_time * SP.nr_normal_halfs()

        if (half_time >= 0
            and SP.nr_normal_halfs() >= 0
            and current_time.cycle() < normal_time
            and current_time.cycle() %  half_time == 1):
            
            self._recovery = SP.recover_init()

