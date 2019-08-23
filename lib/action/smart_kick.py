"""
    \ file smart_kick.py
    \ brief smart kick action class file.
"""

# from lib.math.soccer_math import *
from lib.player.soccer_action import *
#  from lib.player.player_agent import *
from lib.action.kick_table import *
from lib.action.stop_ball import StopBall


class SmartKick(BodyAction):
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

    def execute(self, agent: PlayerAgent):
        dlog.add_text(Level.KICK, "Body_SmartKick")
        wm = agent.world()
        if not wm.self().is_kickable():
            dlog.add_text(Level.KICK, "not kickable")
            return False

        if not wm.ball().velValid():
            dlog.add_text(Level.KICK, "unknown ball vel")
            return StopBall().execute(agent)
        first_speed = min(self._first_speed, ServerParam.i().ball_speed_max())
        first_speed_thr = max(0.0, self._first_speed_thr)
        max_step = max(1, self._max_step)
        if (KickTable.instance().simulate(wm,
                                          self._target_point,
                                          first_speed,
                                          first_speed_thr,
                                          max_step,
                                          self._sequence)
                or self._sequence.speed_ >= first_speed_thr):
            print("kick table true")
            vel = self._sequence.pos_list_[0] - wm.ball().pos()
            kick_accel = vel - wm.ball().vel()
            agent.do_kick(kick_accel.r() / wm.self().kick_rate(),
                          kick_accel.th() - wm.self().body())
            return True
        """
        for p in = self._sequence.pos_list_ :
            dlog.addCircle(p, 0.05)  # how? 
        dlog.addText(Level.KICK," Success!  target=(%.2f %.2f)"
                " speed=%.3f first_speed_thr=%.3f"
                " max_step=%d . achieved_speed=%.3f power=%.2f step=%d",
                self._target_point.x, self._target_point.y,
                first_speed,
                first_speed_thr,
                max_step,
                self._sequence.speed_,
                self._sequence.power_,
                (int)self._sequence.pos_list_.size() )                                                                             
                    
        """
        # TODO: hold_ball mode

        # failed to search the kick sequence

        # Body_HoldBall2008(False, self._target_point, self._target_point).execute(agent)
        return False

    def sequence(self):
        return self._sequence
