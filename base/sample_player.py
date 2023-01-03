from base.decision import get_decision
from lib.player.player_agent import PlayerAgent

class SamplePlayer(PlayerAgent):
    def __init__(self):
        super().__init__()
    
    def action_impl(self):
        get_decision(self)
    