from lib.rcsc.game_time import GameTime
from lib.rcsc.types import SideID, GameModeType
from lib.debug.debug import log


class GameMode:
    def __init__(self, game_mode: GameModeType = GameModeType.BeforeKickOff, time=GameTime()):
        self._game_mode: GameModeType = game_mode
        self._mode_name: str = None
        self._side: SideID = None
        self._time: GameTime = time
        self._left_score: int = 0
        self._right_score: int = 0
        
        if game_mode is not None:
            self._mode_name = self._set_mode_name()
            self._side = self._set_side()
    
    def copy(self):
        new = GameMode()
        new._game_mode = self._game_mode
        new._mode_name = self._mode_name
        new._side = self._side
        new._time = self._time.copy()
        new._left_score = self._left_score
        new._right_score = self._right_score
        
        return new

    def type(self) -> GameModeType:
        return self._game_mode

    def side(self) -> SideID:
        return self._side

    def mode_name(self) -> str:
        return self._mode_name

    def _set_side(self) -> SideID:
        return self._game_mode.side()
    
    def time(self):
        return self._time

    def _set_mode_name(self) -> str:
        if self._game_mode.value[-2:] == '_l' or self._game_mode.value[-2:] == '_r':
            return self._game_mode.value[:-2]
        return self._game_mode.value

    def set_game_mode(self, play_mode: GameModeType):
        self.__init__(play_mode)

    def is_teams_set_play(self, team_side: SideID):
        if team_side == SideID.LEFT:
            if self.type() in [GameModeType.KickOff_Left,
                               GameModeType.KickIn_Left,
                               GameModeType.CornerKick_Left,
                               GameModeType.GoalKick_Left,
                               GameModeType.FreeKick_Left,
                               GameModeType.GoalieCatchBall_Left,
                               GameModeType.IndFreeKick_Left]:
                return True
            return False
        else:
            if self.type() in [GameModeType.KickOff_Right,
                               GameModeType.KickIn_Right,
                               GameModeType.CornerKick_Right,
                               GameModeType.GoalKick_Right,
                               GameModeType.FreeKick_Right,
                               GameModeType.GoalieCatchBall_Right,
                               GameModeType.IndFreeKick_Right]:
                return True
            return False

    def is_penalty_kick_mode(self):
        return self.type() in [
            GameModeType.PenaltySetup_Left,
            GameModeType.PenaltySetup_Right,
            GameModeType.PenaltyReady_Left,
            GameModeType.PenaltyReady_Right,
            GameModeType.PenaltyTaken_Left,
            GameModeType.PenaltyReady_Right,
            GameModeType.PenaltyMiss_Left,
            GameModeType.PenaltyMiss_Right,
            GameModeType.PenaltyScore_Left,
            GameModeType.PenaltyScore_Right,
        ]
        # todo add PlayMode.PenaltyOnfield, PenaltyFoul_

    def is_our_set_play(self, our_side: SideID):
        return self.is_teams_set_play(our_side)

    def update(self, mode: str, current_time: GameTime):
        mode = mode[:mode.find(')')]
        if mode.startswith("yellow") or mode.startswith("red") or mode == 'foul_l' or mode == 'foul_r':
            return False
        
        n_under_line = len(mode.split("_"))
        game_mode: GameModeType = None
        if mode.startswith("goal_l"):
            if n_under_line == 3:
                self._left_score = int(mode.split("_")[-1])
            game_mode = GameModeType.AfterGoal_Left
        elif mode.startswith("goal_r"):
            if n_under_line == 3:
                self._right_score = int(mode.split("_")[-1])
            game_mode = GameModeType.AfterGoal_Right
        
        if game_mode is None:
            game_mode = GameModeType(mode)
        
        if (self._game_mode.is_goalie_catch_ball()
            and game_mode.is_free_kick()
            and self._game_mode.side() == game_mode.side()
            and self._time == current_time):
            
            pass

        else:
            self._game_mode = game_mode
            self._side = self._game_mode.side()
        self._time = current_time.copy()
        return True
    
    def is_server_cycle_stopped_mode(self):
        return self._game_mode in [
            GameModeType.BeforeKickOff,
            GameModeType.AfterGoal_Left,
            GameModeType.AfterGoal_Right,
            GameModeType.OffSide_Left,
            GameModeType.OffSide_Right,
            GameModeType.Foul_Charge_Left,
            GameModeType.Foul_Charge_Right,
            GameModeType.Foul_Push_Left,
            GameModeType.Foul_Push_Right,
            GameModeType.Free_Kick_Fault_Left,
            GameModeType.Free_Kick_Fault_Right,
            GameModeType.Back_Pass_Left,
            GameModeType.Back_Pass_Right,
            GameModeType.CatchFault_Left,
            GameModeType.CatchFault_Right,
            GameModeType.IllegalDefense_Left,
            GameModeType.IllegalDefense_Right,
        ]