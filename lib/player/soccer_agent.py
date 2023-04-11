from lib.player.basic_client import BasicClient


class SoccerAgent:
    def __init__(self):
        self._client: BasicClient = None

    def init(self,
             client: BasicClient,
             goalie: bool = False,
             argv: list = None):
        self._client = client
        self.init_impl(goalie)

    def init_impl(self, goalie: bool) -> bool:
        pass

    def handle_start(self) -> bool:
        pass

    def run(self):
        pass

    def handle_exit(self):
        pass

