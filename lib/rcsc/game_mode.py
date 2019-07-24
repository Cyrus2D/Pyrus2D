from lib.rcsc.types import SideID, PlayMode


class GameMode:
    def __init__(self, game_mode: PlayMode = None):
        self._game_mode: PlayMode = game_mode
        self._mode_name: str = None
        self._side: SideID = None
        if game_mode is not None:
            self._mode_name = self._set_mode_name()
            self._side = self._set_side()

    def mode(self) -> PlayMode:
        return self._game_mode

    def side(self) -> SideID:
        return self._side

    def mode_name(self) -> str:
        return self._mode_name

    def _set_side(self) -> SideID:
        if self._game_mode.value[-2:] == '_l' or self._game_mode.value[-2:] == '_r':
            return SideID(self._game_mode.value[-1])
        return SideID.NEUTRAL

    def _set_mode_name(self) -> str:
        if self._game_mode.value[-2:] == '_l' or self._game_mode.value[-2:] == '_r':
            return self._game_mode.value[:-2]
        return self._game_mode.value

    def set_game_mode(self, play_mode: PlayMode):
        self.__init__(play_mode)

    def is_teams_set_play(self, team_side: SideID):
        mode_name = self.mode_name()
        if mode_name == "kick_off" or \
                mode_name == "kick_in" or \
                mode_name == "corner_kick" or \
                mode_name == "goal_kick" or \
                mode_name == "free_kick" or \
                mode_name == "goalie_catch" or \
                mode_name == "indirect_free_kick":
            return self.side() == team_side
        elif mode_name == "off_side" or \
                mode_name == "foul_charge" or \
                mode_name == "foul_push" or \
                mode_name == "free_kick_fault" or \
                mode_name == "back_pass" or \
                mode_name == "catch_fault":
            return self.side() != team_side
        return False

    def is_our_set_play(self, our_side: SideID):
        return self.is_teams_set_play(our_side)
