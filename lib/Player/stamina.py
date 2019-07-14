import lib.server_param as SP
from lib.Player.player_type import PlayerType


class Stamina:
    def __init__(self, stamina=None, effort=None, recovery=None, capacity=None):
        self._stamina = int(stamina) if stamina else SP.DEFAULT_STAMINA_MAX
        self._effort = int(effort) if effort else SP.DEFAULT_EFFORT_INIT
        self._recovery = int(recovery) if recovery else SP.DEFAULT_RECOVER_INIT
        self._capacity = int(capacity) if capacity else -1

    def init(self, player_type: PlayerType):
        self._stamina = SP.i.stamina_max()
        self._effort = player_type.effort_max()
        self._recovery = SP.i.recover_init()
        self._capacity = SP.i.stamina_capacity()
