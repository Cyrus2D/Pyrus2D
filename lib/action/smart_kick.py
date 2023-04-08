"""
    \ file smart_kick.py
    \ brief smart kick action class file.
"""
from lib.debug.debug import log
from lib.player.soccer_action import *
from lib.action.kick_table import KickTable, Sequence
from lib.action.stop_ball import StopBall
from lib.action.hold_ball import HoldBall
from lib.debug.level import Level
from lib.rcsc.server_param import ServerParam
from pyrusgeom.soccer_math import *


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent

#  from lib.player.player_agent import *
# from pyrusgeom.soccer_math import *


class SmartKick(BodyAction):
    debug_print_DEBUG: bool = True # debug_prints IN SMARTKICK

    def __init__(self, target_point: Vector2D, first_speed, first_speed_thr, max_step):
        super().__init__()
        # target point where the ball should move to
        self._target_point = target_point
        # desired ball first speed
        self._first_speed: float = first_speed
        # threshold value for the ball first speed
        self._first_speed_thr: float = first_speed_thr
        # maximum number of kick steps
        self._max_step: int = max_step
        # result kick sequence holder
        self._sequence = Sequence()

    def execute(self, agent: 'PlayerAgent'):
        log.sw_log().kick().add_text( "Body_SmartKick")
        log.os_log().debug(f'c{agent.world().time().cycle()}kick{self._target_point} {self._first_speed}')
        log.sw_log().kick().add_text(f'c{agent.world().time().cycle()}kick{self._target_point} {self._first_speed}')
        wm = agent.world()
        if not wm.self().is_kickable():
            if SmartKick.debug_print_DEBUG:
                log.os_log().info("----- NotKickable -----")
                log.sw_log().kick().add_text("not kickable")
            return False
        if not wm.ball().vel_valid():
            if SmartKick.debug_print_DEBUG:
                log.os_log().info("-- NonValidBall -> StopBall --")
                log.sw_log().kick().add_text("unknown ball vel")
            return StopBall().execute(agent)
        first_speed = min(self._first_speed, ServerParam.i().ball_speed_max())
        first_speed_thr = max(0.0, self._first_speed_thr)
        max_step = max(1, self._max_step)
        ans = KickTable.instance().simulate(wm,
                                            self._target_point,
                                            first_speed,
                                            first_speed_thr,
                                            max_step,
                                            self._sequence)
        if ans[0] and SmartKick.debug_print_DEBUG:
            log.os_log().info(f"Smart kick : {ans[0]} seq -> speed : {ans[1].speed_} power : {ans[1].power_} score : {ans[1].score_} flag : {ans[1].flag_} next_pos : {ans[1].pos_list_[0]} {len(ans[1].pos_list_)} step {ans[1].pos_list_}")
            log.sw_log().kick().add_text(f"Smart kick : {ans[0]} seq -> speed : {ans[1].speed_} power : {ans[1].power_} score : {ans[1].score_} flag : {ans[1].flag_} next_pos : {ans[1].pos_list_[0]} {len(ans[1].pos_list_)} step {ans[1].pos_list_}")

        if ans[0]:
            self._sequence = ans[1]
            if self._sequence.speed_ >= first_speed_thr:  # double check
                vel = self._sequence.pos_list_[0] - wm.ball().pos()
                kick_accel = vel - wm.ball().vel()
                if SmartKick.debug_print_DEBUG:
                    log.os_log().debug(f"Kick Vel : {vel}, Kick Power : {kick_accel.r() / wm.self().kick_rate()}, Kick Angle : {kick_accel.th() - wm.self().body()}")
                    log.sw_log().kick().add_text(f"Kick Vel : {vel}, Kick Power : {kick_accel.r() / wm.self().kick_rate()}, Kick Angle : {kick_accel.th() - wm.self().body()}")

                agent.do_kick(kick_accel.r() / wm.self().kick_rate(),
                              kick_accel.th() - wm.self().body())
                if SmartKick.debug_print_DEBUG:
                    log.os_log().debug(f"----------------#### Player Number {wm.self().unum()} 'DO_KICK'ed in SmartKick at Time: {wm.time().cycle()} ####----------------")
                    log.sw_log().kick().add_text(f"----------------#### Player Number {wm.self().unum()} 'DO_KICK'ed in SmartKick at Time: {wm.time().cycle()} ####----------------")
                return True

        # failed to search the kick sequence
        log.sw_log().kick().add_text("----->>>>>Hold Ball")
        HoldBall(False, self._target_point, self._target_point).execute(agent)
        return False

    def sequence(self):
        return self._sequence
