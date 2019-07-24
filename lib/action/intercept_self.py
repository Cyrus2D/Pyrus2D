from lib.player.world_model import WorldModel


class SelfIntercept:
    def __init__(self, wm: WorldModel, ball_cache):
        self._wm = wm
        self._ball_cache = ball_cache

    def predict(self, max_cycle, self_cache):
        