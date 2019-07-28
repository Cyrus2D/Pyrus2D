import copy

from lib.rcsc.player_type import PlayerType
from lib.rcsc.server_param import ServerParam


class StaminaModel:
    def __init__(self, stamina=None, effort=None, recovery=None, capacity=None):
        SP = ServerParam.i()
        self._stamina: float = float(stamina) if stamina else SP.stamina_max()
        self._effort: float = float(effort) if effort else SP.effort_init()
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

        stamina_inc = min(player_type.stamina_inc_max() * self._recovery, SP.stamina_max() - self._stamina)
        if SP.stamina_capacity() >= 0:
            self._stamina += min(stamina_inc, self._capacity)
            self._capacity -= stamina_inc
            self._capacity = max(0, self._capacity)
        else:
            self._stamina += stamina_inc
        self._stamina = min(self._stamina, SP.stamina_max())  # kirm tu in mohasebat :|

    def capacity_is_empty(self) -> bool:
        return 0 <= self._capacity <= 1e-5

    def simulate_dash(self, player_type: PlayerType, dash_power: float):
        self._stamina -= dash_power if dash_power >= 0 else dash_power * -2
        self._stamina = max(0, self._stamina)
        self.simulate_wait(player_type)

    def copy(self):
        new = copy.deepcopy(self)
        return new

    def stamina(self):
        return self._stamina

    def effort(self):
        return self._effort

    def recovery(self):
        return self._recovery

    def capacity(self):
        return self._capacity
