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

    def assign(self, c: int, s: int):
        self._cycle = c
        self._stopped_cycle = s
        return self

    def __repr__(self):
        return f"({self._cycle}, {self._stopped_cycle})"

    def __eq__(self, other):
        return self.cycle() == other.cycle() and self.stopped_cycle() == other.stopped_cycle()

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        return True if self.cycle() > other.cycle() or (self.cycle() == other.cycle() and self.stopped_cycle() > other.stopped_cycle()) else False

    def copy(self):
        return GameTime(self._cycle, self._stopped_cycle)

    def __str__(self):
        return f'GameTime cycle {self._cycle}.{self._stopped_cycle}'
