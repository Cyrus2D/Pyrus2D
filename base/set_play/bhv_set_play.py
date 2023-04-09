from base.set_play.bhv_set_play_before_kick_off import Bhv_BeforeKickOff
from base.strategy_formation import *
from lib.action.neck_scan_players import NeckScanPlayers
from lib.action.neck_turn_to_ball_or_scan import NeckTurnToBallOrScan
from lib.action.scan_field import ScanField
from lib.debug.debug import log
from lib.debug.level import Level
from lib.action.go_to_point import *
from lib.messenger.pass_messenger import PassMessenger
from lib.rcsc.types import GameModeType
from base.generator_action import KickAction
from base.generator_pass import BhvPassGen
from lib.action.smart_kick import SmartKick

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.object_player import PlayerObject
    from lib.player.player_agent import PlayerAgent


class Bhv_SetPlay:
    _kickable_time: int = -1
    _waiting = False
    def __init__(self):
        pass

    def execute(self, agent: 'PlayerAgent'):
        if self.kick(agent):
            return True
        
        log.sw_log().team().add_text( "Bhv_SetPlay")
        wm: WorldModel = agent.world()
        game_mode = wm.game_mode().type()
        game_side = wm.game_mode().side()

        if game_mode is GameModeType.BeforeKickOff or game_mode.is_after_goal():
            return Bhv_BeforeKickOff().execute(agent)

        st = StrategyFormation.i()
        target = st.get_pos(wm.self().unum())
        if wm.game_mode().side() is wm.our_side():
            nearest_tm_dist = 1000
            nearest_tm = 0
            for i in range(1, 12):
                tm: 'PlayerObject' = wm.our_player(i)
                if tm is None:
                    continue
                if tm.unum() == i:
                    dist = tm.pos().dist(wm.ball().pos())
                    if dist < nearest_tm_dist:
                        nearest_tm_dist = dist
                        nearest_tm = i
            if nearest_tm is wm.self().unum():
                target = wm.ball().pos()
        if GoToPoint(target, 0.5, 100).execute(agent):
            agent.set_neck_action(NeckTurnToBallOrScan())
            return True
        else:
            ScanField().execute(agent)
            return True

    @staticmethod
    def is_kicker(agent):
        wm = agent.world()
        if wm.game_mode().mode_name() == "goalie_catch" and \
                wm.game_mode().side() == wm.our_side() and \
                not wm.self().goalie():
            log.sw_log().team().add_text( "(is_kicker) goalie free kick")
            return False
        if not wm.self().goalie() and \
                wm.game_mode().mode_name() == "goal_kick" and \
                wm.game_mode().side() == wm.our_side():
            return False
        if wm.self().goalie() and \
                wm.game_mode().mode_name() == "goal_kick" and \
                wm.game_mode().side() == wm.our_side():
            return True
        st = StrategyFormation().i()
        kicker_unum = 0
        min_dist2 = 1000000
        second_kicker_unum = 0
        second_min_dist2 = 1000000
        for unum in range(1, 12):
            if unum == wm.our_goalie_unum():
                continue

            home_pos = st.get_pos(unum)
            if not home_pos.is_valid():
                continue

            d2 = home_pos.dist2(wm.ball().pos())
            if d2 < second_min_dist2:
                second_kicker_unum = unum
                second_min_dist2 = d2

                if second_min_dist2 < min_dist2:
                    # swaping (fun in python :))
                    second_min_dist2, min_dist2 = min_dist2, second_min_dist2
                    second_kicker_unum, kicker_unum = kicker_unum, second_kicker_unum

        log.sw_log().team().add_text( f"(is kicker) kicker_unum={kicker_unum}, second_kicker_unum={second_kicker_unum}")

        kicker: 'PlayerObject' = None
        second_kicker: 'PlayerObject' = None

        if kicker_unum != 0:
            kicker = wm.our_player(kicker_unum)
        if second_kicker_unum != 0:
            second_kicker = wm.our_player(second_kicker_unum)

        if kicker is None:
            if len(wm.teammates_from_ball()) > 0 and \
                    wm.teammates_from_ball()[0].dist_from_ball() < wm.ball().dist_from_self() * 0.9:
                log.sw_log().team().add_text( "(is kicker) first kicker")
                return False

            log.sw_log().team().add_text( "(is_kicker) self(1)")
            return True

        if kicker is not None and \
                second_kicker is not None and \
                (kicker.unum() == wm.self().unum() or \
                 second_kicker.unum() == wm.self().unum()):
            if min_dist2 ** 0.5 < (second_min_dist2 ** 0.5) * 0.95:
                log.sw_log().team().add_text( f"(is kicker) kicker->unum={kicker.unum()} (1)")
                return kicker.unum() == wm.self().unum()
            elif kicker.dist_from_ball() < second_kicker.dist_from_ball() * 0.95:
                log.sw_log().team().add_text( f"(is kicker) kicker->unum={kicker.unum()} (2)")
                return kicker.unum() == wm.self().unum()
            elif second_kicker.dist_from_ball() < kicker.dist_from_ball() * 0.95:
                log.sw_log().team().add_text( f"(is kicker) kicker->unum={kicker.unum()} (3)")
                return second_kicker.unum() == wm.self().unum()
            elif len(wm.teammates_from_ball()) > 0 and \
                    wm.teammates_from_ball()[0].dist_from_ball() < wm.self().dist_from_ball() * 0.95:
                log.sw_log().team().add_text( "(is kicker) other kicker")
                return False
            else:
                log.sw_log().team().add_text( "(is kicker) self (2)")
                return True
        return kicker.unum() == wm.self().unum()
    
    def kick(self, agent: 'PlayerAgent'):
        wm = agent.world()

        if not wm.self().is_kickable():
            return False

        if not Bhv_SetPlay._waiting:
            Bhv_SetPlay._kickable_time = wm.time().cycle()
            Bhv_SetPlay._waiting = True

        if Bhv_SetPlay._waiting and wm.time().cycle() - Bhv_SetPlay._kickable_time > 30:
            Bhv_SetPlay._waiting = False
        else:
            ScanField().execute(agent)
            return True

        action_candidates: list[KickAction] = []
        action_candidates += BhvPassGen().generator(wm)
        if len(action_candidates) == 0:
            return False

        best_action: KickAction = max(action_candidates)

        target = best_action.target_ball_pos
        log.debug_client().set_target(target)
        log.debug_client().add_message(f'{best_action.type.value} to {best_action.target_ball_pos} {best_action.start_ball_speed}')
        SmartKick(target, best_action.start_ball_speed, best_action.start_ball_speed - 1, 3).execute(agent)
        agent.add_say_message(PassMessenger(best_action.target_unum,
                                            best_action.target_ball_pos,
                                            agent.effector().queued_next_ball_pos(),
                                            agent.effector().queued_next_ball_vel()))

        agent.set_neck_action(NeckScanPlayers())
        return True
