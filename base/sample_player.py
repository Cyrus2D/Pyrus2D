from base.decision import get_decision
from base.view_tactical import ViewTactical
from lib.action.neck_body_to_ball import NeckBodyToBall
from lib.action.neck_turn_to_ball_or_scan import NeckTurnToBallOrScan
from lib.action.scan_field import ScanField
from lib.player.player_agent import PlayerAgent
from lib.rcsc.types import GameModeType


class SamplePlayer(PlayerAgent):
    def __init__(self):
        super().__init__()
    
    def action_impl(self):
        if self.do_preprocess():
            return

        get_decision(self)

    def do_preprocess(self):
        wm = self.world()

        if wm.self().is_frozen():
            self.set_view_action(ViewTactical())
            self.set_neck_action(NeckTurnToBallOrScan())
            return True

        if not wm.self().pos_valid():
            self.set_view_action(ViewTactical())
            ScanField().execute(self)
            return True

        count_thr = 10 if wm.self().goalie() else 5
        if wm.ball().pos_count() > count_thr or ( wm.game_mode().type() is not GameModeType.PlayOn and wm.ball().seen_pos_count() > count_thr + 10):
            self.set_view_action(ViewTactical())
            NeckBodyToBall().execute(self)
            return True

        self.set_view_action(ViewTactical())

        return False
