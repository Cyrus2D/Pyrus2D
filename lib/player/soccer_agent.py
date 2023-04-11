from lib.player.basic_client import BasicClient


class SoccerAgent:
    def __init__(self):
        self._client: BasicClient = BasicClient()

    def init_impl(self, goalie: bool) -> bool:
        pass

    def handle_start(self) -> bool:
        pass

    def run(self):
        pass

    def handle_exit(self):
        pass

