from lib.debug.debug import log
from lib.debug.level import Level
from pyrusgeom.vector_2d import Vector2D
from lib.player.trainer_agent import TrainerAgent
from lib.rcsc.types import GameModeType


class SampleTrainer(TrainerAgent):
    def __init__(self):
        super().__init__()

    def action_impl(self):
        if self.world().team_name_left() == "":  # TODO left team name...  # TODO is empty...
            self.do_teamname()
            return
        self.sample_action()

    def sample_action(self):
        log.sw_log().block().add_text( "Sample Action")

        wm = self.world()
        ballpos = wm.ball().pos()
        if ballpos.abs_x() > 10 or ballpos.abs_y() > 10:
            for i in range(1, 12):
                self.do_move_player(wm.team_name_l(), i, Vector2D(-40, i * 5 - 30))
            self.do_move_ball(Vector2D(0, 0), Vector2D(0, 0))
            self.do_change_mode(GameModeType.PlayOn)
