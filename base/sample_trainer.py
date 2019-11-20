from base.decision import get_decision
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.vector_2d import Vector2D
from lib.player.trainer_agent import TrainerAgent


class SampleTrainer(TrainerAgent):
    def __init__(self):
        super().__init__()

    def action_impl(self):
        if self.world().team_name() is None:  # TODO left team name...  # TODO is empty...
            self.do_teamname()
            return
        self.sample_action()

    def sample_action(self):
        dlog.add_text(Level.BLOCK, "Sample Action")

        wm = self.world()
        ballpos = wm.ball().pos()
        if ballpos.absX() > 10 or ballpos.absY() > 10:
            for i in range(1, 12):
                self.do_move_player(wm.team_name(), i, Vector2D(-40, i * 5 - 30))
            self.do_move_ball(Vector2D(0, 0), Vector2D(0, 0))

        else:
            get_decision(self)
