from enum import Enum, unique, auto

from lib.debug.debug import log
from lib.debug.level import Level
from lib.rcsc.game_time import GameTime
from lib.rcsc.types import ViewWidth

DEBUG: bool = True


class SeeState:
    def __init__(self):
        self._current_time: GameTime = GameTime(-1, 0)
        self._last_see_time: GameTime = GameTime(-1, 0)
        self._cycles_till_next_see: int = 100
        self._view_width: ViewWidth = ViewWidth(ViewWidth.NORMAL)

    def update_by_sense_body(self, sense_time: GameTime, vw: ViewWidth):
        self.set_new_cycle(sense_time)

        if self._view_width != vw:
            if DEBUG:
                log.sw_log().system().add_text(f"see state: (update by sense body)"
                                               f"vew_width does not match."
                                               f" old={self._view_width}, new={vw}")
                log.os_log().info(f"see state: (update by sense body)"
                                  f"vew_width does not match."
                                  f" old={self._view_width}, new={vw}")
            self._view_width = vw

    def update_by_see(self, see_time: GameTime, vw: ViewWidth):
        self.set_new_cycle(see_time)
        self._last_see_time = see_time.copy()
        self._cycles_till_next_see = 0
        self.set_view_mode(vw)

    def set_new_cycle(self, new_time: GameTime):
        if new_time == self._current_time:
            return
        self._current_time = new_time.copy()

        self._cycles_till_next_see -= 1
        if self._cycles_till_next_see < 0:
            self._cycles_till_next_see = 0

    def set_view_mode(self, new_width: ViewWidth):
        if self._last_see_time != self._current_time:
            if DEBUG:
                log.sw_log().system().add_text("see state (set_view_mode) no current cycle see arrival")
            return

        self._view_width = new_width

        if new_width == ViewWidth.WIDE:
            self._cycles_till_next_see = 3
        elif new_width == ViewWidth.NORMAL:
            self._cycles_till_next_see = 2
        elif new_width == ViewWidth.NARROW:
            self._cycles_till_next_see = 1

        log.sw_log().system().add_text(f"see state (set_view_mode)"
                                       f" synch {new_width}: cycle = {self._cycles_till_next_see}")
        return

    def cycles_till_next_see(self):
        return self._cycles_till_next_see
