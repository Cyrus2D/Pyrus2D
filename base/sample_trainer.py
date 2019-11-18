from lib.player.trainer_agent import TrainerAgent


class SamplePlayer(TrainerAgent):
    def __init__(self):
        super().__init__()

    def action_impl(self):
        if self.world().team_name() is None:  # TODO left team name...  # TODO is empty...
            self.do_teamname()
            return
        self.sample_action()
