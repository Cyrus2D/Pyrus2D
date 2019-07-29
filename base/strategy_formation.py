from lib.formation.delaunay_triangulation import *
import os

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

    def update(self, wm):
        ball_pos = wm.ball().pos()
        self.defense_formation.update(ball_pos)

    def get_pos(self, unum):
        return self.defense_formation.get_pos(unum)


class StrategyFormation:
    _i: _StrategyFormation = _StrategyFormation()

    @staticmethod
    def i() -> _StrategyFormation:
        return StrategyFormation._i
