from base.decision import get_decision
from base.sample_communication import SampleCommunication
from base.view_tactical import ViewTactical
from lib.action.go_to_point import GoToPoint
from lib.action.intercept import Intercept
from lib.action.neck_body_to_ball import NeckBodyToBall
from lib.action.neck_turn_to_ball import NeckTurnToBall
from lib.action.neck_turn_to_ball_or_scan import NeckTurnToBallOrScan
from lib.action.scan_field import ScanField
from lib.debug.debug import log
from lib.debug.level import Level
from lib.player.player_agent import PlayerAgent
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import GameModeType


class SamplePlayer(PlayerAgent):
    def __init__(self):
        super().__init__()

        self._communication = SampleCommunication()
    
    def action_impl(self):
        wm = self.world()
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

        count_thr = 10 if wm.self().goalie else 5
        if wm.ball().pos_count > count_thr or ( wm.game_mode().type() is not GameModeType.PlayOn and wm.ball().seen_pos_count > count_thr + 10):
            self.set_view_action(ViewTactical())
            NeckBodyToBall().execute(self)
            return True

        self.set_view_action(ViewTactical())

        if self.do_heard_pass_receive():
            return True

        return False

    def do_heard_pass_receive(self):
        wm = self.world()

        if wm.messenger_memory().pass_time() != wm.time() \
            or len(wm.messenger_memory().pass_()) == 0 \
            or wm.messenger_memory().pass_()[0]._receiver != wm.self().unum:

            return False

        self_min = wm.intercept_table().self_reach_cycle()
        intercept_pos = wm.ball().inertia_point(self_min)
        heard_pos = wm.messenger_memory().pass_()[0]._pos

        log.sw_log().team().add_text( f"(sample palyer do heard pass) heard_pos={heard_pos}, intercept_pos={intercept_pos}")

        if not wm.kickable_teammate() \
            and wm.ball().pos_count <= 1 \
            and wm.ball().vel_count <= 1 \
            and self_min < 20:
            log.sw_log().team().add_text( f"(sample palyer do heard pass) intercepting!, self_min={self_min}")
            log.debug_client().add_message("Comm:Receive:Intercept")
            Intercept().execute(self)
            self.set_neck_action(NeckTurnToBall())
        else:
            log.sw_log().team().add_text( f"(sample palyer do heard pass) go to point!, cycle={self_min}")
            log.debug_client().set_target(heard_pos)
            log.debug_client().add_message("Comm:Receive:GoTo")

            GoToPoint(heard_pos, 0.5, ServerParam.i().max_dash_power()).execute(self)
            self.set_neck_action(NeckTurnToBall())

        # TODO INTENTION?!?
























