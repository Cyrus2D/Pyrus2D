from enum import Enum, unique, auto

from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.rcsc.game_time import GameTime
from lib.rcsc.types import ViewWidth, ViewQuality
from lib.debug.debug_print import debug_print

DEBUG: bool = True


@unique
class SynchType(Enum):
    SYNCH_NO = auto()
    SYNCH_EVERY = auto()
    SYNCH_NARROW = auto()
    SYNCH_NORMAL = auto()
    SYNCH_WIDE = auto()
    SYNCH_SYNC = auto()


@unique
class Timing(Enum):
    TIME_0_00 = 0
    TIME_37_5 = 375
    TIME_75_0 = 750
    TIME_12_5 = 125
    TIME_50_0 = 500
    TIME_87_5 = 875
    TIME_22_5 = 225
    TIME_62_5 = 625
    TIME_SYNC = 999
    TIME_NOSYNCH = 1000


class SeeState:
    HISTORY_SIZE: int = 3
    _synch_see_mode: bool = True

    def __init__(self):
        self._current_time: GameTime = GameTime(-1, 0)
        self._last_see_time: GameTime = GameTime(-1, 0)
        self._synch_type: SynchType = SynchType(SynchType.SYNCH_NO)
        self._last_timing: Timing = Timing(Timing.TIME_NOSYNCH)
        self._current_see_count: int = 0
        self._cycles_till_next_see: int = 100
        self._view_width: ViewWidth = ViewWidth(ViewWidth.NORMAL)
        self._view_quality: ViewQuality = ViewQuality(ViewQuality.HIGH)

        self._see_count_history: list = [0 for i in range(SeeState.HISTORY_SIZE)]

    def set_synch_mode(self):
        SeeState._synch_see_mode = True

    @staticmethod
    def synch_see_mode():
        return SeeState._synch_see_mode

    def last_timing(self):
        return self._last_timing

    def update_by_sense_body(self, sense_time: GameTime, vw: ViewWidth, vq: ViewQuality):
        self.set_new_cycle(sense_time)

        if self._view_width != vw:
            dlog.add_text(Level.SYSTEM, f"see state: (update by sense body)"
                                        f"vew_width does not match."
                                        f" old={self._view_width}, new={vw}")
            self._view_width = vw

        if self._view_quality != vq:
            dlog.add_text(Level.SYSTEM, f"see state: (update by sense body)"
                                        f"vew_width does not match."
                                        f" old={self._view_quality}, new={vq}")
            self._view_quality = vq

    def update_by_see(self, see_time: GameTime, vw: ViewWidth, vq: ViewQuality):
        if see_time == self._last_see_time:
            self._current_see_count += 1
            if self.is_synch():
                dlog.add_text(Level.SYSTEM, "see_state: update after see: estimated synch, but duplicated")
        else:
            self.set_new_cycle(see_time)
            self._last_see_time = see_time
            self._current_see_count = 1

        if vq == ViewQuality.LOW:
            self._last_timing = Timing.TIME_NOSYNCH
            return

        if not self.is_synch():
            dlog.add_text(Level.SYSTEM, "see state: update by see: but no synch")
            return

        if self._cycles_till_next_see > 0:
            self._cycles_till_next_see = 0
            self.set_view_mode(vw, vq)

        new_timing: Timing = self._get_next_timing(vw, vq)
        if new_timing == Timing.TIME_NOSYNCH:
            debug_print(f"time: {see_time}, invalid view width. no synchronization...")

        dlog.add_text(Level.SYSTEM, f"see state: (update by seee) see update,"
                                    f"last time: {self._last_timing},"
                                    f"current time: {new_timing}")

        self._last_timing = new_timing

    def set_new_cycle(self, new_time: GameTime):
        if new_time == self._current_time:
            return
        self._current_time = new_time.copy()

        self._cycles_till_next_see -= 1
        if self._cycles_till_next_see < 0:
            self._cycles_till_next_see = 0

        # for i in range(SeeState.HISTORY_SIZE - 1, 0, -1):
        #     self._see_count_history[i] = self._see_count_history[i - 1]
        # self._see_count_history[0] = self._current_see_count

        # Python way:
        self._see_count_history.pop(0)
        self._see_count_history.append(self._current_see_count)

        self._current_see_count = 0

    def set_last_see_timing(self, last_timing: Timing):
        self._last_timing = last_timing

    def is_synched_see_count_normal_mode(self):
        return (self._see_count_history[0] == 2
                and self._see_count_history[1] == 3)

    def is_synched_see_count_synch_mode(self):
        return (self._current_see_count == 2
                and self._see_count_history[0] == 3
                and self._see_count_history[1] == 2
                and self._see_count_history[2] == 3)

    def set_view_mode(self, new_width: ViewWidth, new_quality: ViewQuality):
        if self._last_see_time != self._current_time:
            if DEBUG:
                dlog.add_text(Level.SYSTEM, "see state (set_view_mode) no current cycle see arrival")
            return

        self._view_width = new_width
        self._view_quality = new_quality

        if SeeState._synch_see_mode:
            if new_width == ViewWidth.WIDE:
                self._cycles_till_next_see = 3
                self._synch_type = SynchType.SYNCH_WIDE

            elif new_width == ViewWidth.NORMAL:
                self._cycles_till_next_see = 2
                self._synch_type = SynchType.SYNCH_NORMAL

            elif new_width == ViewWidth.NARROW:
                self._cycles_till_next_see = 1
                self._synch_type = SynchType.SYNCH_NARROW

            dlog.add_text(Level.SYSTEM, f"see state (set_view_mode)"
                                        f" synch {new_width}: cycle = {self._cycles_till_next_see}")
            return

        if self._last_timing == Timing.TIME_0_00:
            if new_width == ViewWidth.WIDE:
                self._cycles_till_next_see = 3
                self._synch_type = SynchType.SYNCH_WIDE
            elif new_width == ViewWidth.NORMAL:
                self._cycles_till_next_see = 1
                self._synch_type = SynchType.SYNCH_EVERY
            elif new_width == ViewWidth.NARROW:
                debug_print(f"{self._current_time} SeeState. TIME_0_00. Narrow is illegal.")
                self._synch_type = SynchType.SYNCH_NO
            dlog.add_text(Level.SYSTEM,
                          f"see state (setViewMode) 00:{new_width}: cycle = {self._cycles_till_next_see}")
            return

        if self._last_timing == Timing.TIME_50_0:
            if new_width == ViewWidth.WIDE:
                self._cycles_till_next_see = 3
                self._synch_type = SynchType.SYNCH_WIDE
            elif new_width == ViewWidth.NORMAL:
                self._cycles_till_next_see = 2
                self._synch_type = SynchType.SYNCH_NORMAL
            elif new_width == ViewWidth.NARROW:
                self._cycles_till_next_see = 1
                self._synch_type = SynchType.SYNCH_EVERY
            dlog.add_text(Level.SYSTEM,
                          f"see state (setViewMode) 50:{new_width}: cycle = {self._cycles_till_next_see}")
            return

        if self._last_timing == Timing.TIME_22_5:
            if new_width == ViewWidth.WIDE:
                self._cycles_till_next_see = 3
                self._synch_type = SynchType.SYNCH_WIDE
            elif new_width == ViewWidth.NORMAL:
                debug_print(f"{self._current_time} SeeState. TIME_22_5. Normal is illegal.")
                self._synch_type = SynchType.SYNCH_NO
            elif new_width == ViewWidth.NARROW:
                self._cycles_till_next_see = 1
                self._synch_type = SynchType.SYNCH_EVERY
            dlog.add_text(Level.SYSTEM,
                          f"see state (setViewMode) 50:{new_width}: cycle = {self._cycles_till_next_see}")
            return

        self._synch_type = SynchType.SYNCH_NO
        if new_width == ViewWidth.WIDE:
            self._cycles_till_next_see = 3
        elif new_width == ViewWidth.NORMAL:
            self._cycles_till_next_see = 2
        elif new_width == ViewWidth.NARROW:
            self._cycles_till_next_see = 1

    def can_change_view_to(self, next_width: ViewWidth, current: GameTime):
        if current != self._last_see_time:
            return False

        if SeeState._synch_see_mode:
            return True

        if next_width == ViewWidth.NARROW:
            if self._last_timing == Timing.TIME_0_00:
                return False
            return True

        if next_width == ViewWidth.NORMAL:
            if self._last_timing == Timing.TIME_0_00 or self._last_timing == Timing.TIME_50_0:
                return True
            return False

        if next_width == ViewWidth.WIDE:
            return True
        debug_print("see state (can_change_view) unexpected reeach...")
        return True

    def cycles_till_next_see(self):
        return self._cycles_till_next_see

    def is_synch(self) -> bool:
        if SeeState._synch_see_mode:
            return True

        if self._synch_type == SynchType.SYNCH_SYNC:
            return True

        return (self._last_timing == Timing.TIME_0_00
                or self._last_timing == Timing.TIME_50_0
                or self._last_timing == Timing.TIME_22_5)

    def _get_next_timing(self, vw: ViewWidth, vq: ViewQuality):
        if SeeState._synch_see_mode:
            return Timing.TIME_SYNC

        if vq == ViewQuality.LOW:
            return Timing.TIME_NOSYNCH

        timing = Timing.TIME_NOSYNCH

        if self.last_timing() == Timing.TIME_0_00:
            if vw == ViewWidth.WIDE:
                timing = Timing.TIME_0_00
            elif vw == ViewWidth.NORMAL:
                timing = Timing.TIME_50_0
            elif vw == ViewWidth.NARROW:
                timing = Timing.TIME_NOSYNCH

        elif self.last_timing() == Timing.TIME_50_0:
            if vw == ViewWidth.WIDE:
                timing = Timing.TIME_50_0
            elif vw == ViewWidth.NORMAL:
                timing = Timing.TIME_0_00
            elif vw == ViewWidth.NARROW:
                timing = Timing.TIME_22_5

        elif self.last_timing() == Timing.TIME_22_5:
            if vw == ViewWidth.WIDE:
                timing = Timing.TIME_22_5
            elif vw == ViewWidth.NORMAL:
                timing = Timing.TIME_NOSYNCH
            elif vw == ViewWidth.NARROW:
                timing = Timing.TIME_0_00

        return timing
