from lib.formation.delaunay_triangulation import *
from lib.player.templates import *
import os
from enum import Enum


class Situation(Enum):
    OurSetPlay_Situation = 0,
    OppSetPlay_Situation = 1,
    Defense_Situation = 2,
    Offense_Situation = 3,
    PenaltyKick_Situation = 4


class _StrategyFormation:
    def __init__(self):
        pwd = '.'
        if "base" in os.listdir('.'):
            pwd = 'base'
        self.before_kick_off_formation: Formation = Formation(f'{pwd}/formation_dt/before_kick_off.conf')
        self.defense_formation: Formation = Formation(f'{pwd}/formation_dt/defense_formation.conf')
        self.offense_formation: Formation = Formation(f'{pwd}/formation_dt/offense_formation.conf')
        self.goalie_kick_opp_formation: Formation = Formation(f'{pwd}/formation_dt/goalie_kick_opp_formation.conf')
        self.goalie_kick_our_formation: Formation = Formation(f'{pwd}/formation_dt/goalie_kick_our_formation.conf')
        self.kickin_our_formation: Formation = Formation(f'{pwd}/formation_dt/kickin_our_formation.conf')
        self.setplay_opp_formation: Formation = Formation(f'{pwd}/formation_dt/setplay_opp_formation.conf')
        self.setplay_our_formation: Formation = Formation(f'{pwd}/formation_dt/setplay_our_formation.conf')
        self._poses = [Vector2D(0, 0) for i in range(11)]
        self.current_situation = Situation.Offense_Situation
        self.current_formation = self.offense_formation

    def update(self, wm: WorldModel):
        if wm.game_mode().type() is GameModeType.PlayOn:
            self.current_situation = Situation.Offense_Situation # Todo add deffense situation
        else:
            if wm.game_mode().is_penalty_kick_mode():
                self.current_situation = Situation.PenaltyKick_Situation
            elif wm.game_mode().is_our_set_play(wm.our_side()):
                self.current_situation = Situation.OurSetPlay_Situation
            else:
                self.current_situation = Situation.OppSetPlay_Situation

        ball_pos = wm.ball().pos()

        if wm.game_mode().type() is GameModeType.PlayOn:
            if self.current_situation is Situation.Offense_Situation:
                self.current_formation = self.offense_formation
            else:
                self.current_formation = self.defense_formation

        elif wm.game_mode().type() in [GameModeType.BeforeKickOff, GameModeType.AfterGoal_Left,
                                       GameModeType.AfterGoal_Right]:
            self.current_formation = self.before_kick_off_formation

        elif wm.game_mode().type() in [GameModeType.GoalKick_Left, GameModeType.GoalKick_Right]: # Todo add Goal Catch!!
            if wm.game_mode().is_our_set_play(wm.our_side()):
                self.current_formation = self.goalie_kick_our_formation
            else:
                self.current_formation = self.goalie_kick_opp_formation

        else:
            if wm.game_mode().is_our_set_play(wm.our_side()):
                if wm.game_mode().type() in [GameModeType.KickIn_Right, GameModeType.KickIn_Left,
                                             GameModeType.CornerKick_Right, GameModeType.CornerKick_Left]:
                    self.current_formation = self.kickin_our_formation
                else:
                    self.current_formation = self.setplay_our_formation
            else:
                self.current_formation = self.setplay_opp_formation

        self.current_formation.update(ball_pos)
        self._poses = self.current_formation.get_poses()

        if self.current_formation is self.before_kick_off_formation or wm.game_mode().type() in \
                [GameModeType.KickOff_Left, GameModeType.KickOff_Right]:
            for pos in self._poses:
                pos._x = min(pos.x(), -0.5)
        else:
            pass # Todo add offside line
            # for pos in self._poses:
            #     pos._x = math.min(pos.x(), )

    def get_pos(self, unum):
        return self._poses[unum - 1]


class StrategyFormation:
    _i: _StrategyFormation = _StrategyFormation()

    @staticmethod
    def i() -> _StrategyFormation:
        return StrategyFormation._i
