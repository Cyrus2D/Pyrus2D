from lib.player.basic_client import BasicClient


class SoccerAgent:
    def __init__(self):
        pass

    def init(self,
             client: BasicClient,
             argv: list) -> bool:
        pass

    def init_impl(self,
                  cmd_parser: CmdLineParser) -> bool:
        pass

    def handle_start(self) -> bool:
        pass

    def handle_message(self):
