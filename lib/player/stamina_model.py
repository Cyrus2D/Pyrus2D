import lib.rcsc.server_param as SP
from lib.rcsc.player_type import PlayerType


class StaminaModel:
    def __init__(self, stamina=None, effort=None, recovery=None, capacity=None):
        self._stamina: float = float(stamina) if stamina else SP.DEFAULT_STAMINA_MAX
        self._effort: float = float(effort) if effort else SP.DEFAULT_EFFORT_INIT
        self._recovery: float = float(recovery) if recovery else SP.DEFAULT_RECOVER_INIT
        self._capacity: float = float(capacity) if capacity else -1

    def init(self, player_type: PlayerType):
        self._stamina = SP.i.stamina_max()
        self._effort = player_type.effort_max()
        self._recovery = SP.i.recover_init()
        self._capacity = SP.i.stamina_capacity()

    def stamina(self):
        return self._stamina

    def effort(self):
        return self._effort

    def recovery(self):
        return self._recovery

    def capacity(self):
        return self._capacity
