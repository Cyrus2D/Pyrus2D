class GameTime:
    def __init__(self, cycle: int = 0, stopped_cycle: int = 0):
        self._cycle = cycle
        self._stopped_cycle = stopped_cycle

    def cycle(self):
        return self._cycle

    def stopped_cycle(self):
        return self._stopped_cycle

    def add_cycle(self, cycle: int):
        self._cycle += cycle

    def add_stopped_cycle(self, stopped_cycle):
        self._stopped_cycle += stopped_cycle

    def __repr__(self):
        return f"{self.cycle()}"

    def __eq__(self, other):
        return self.cycle() == other.cycle()

    def copy(self):
        return GameTime(self._cycle, self._stopped_cycle)
