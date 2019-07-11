class PlayerInit:
    def __init__(self, team_name, version=None):
        self._team_name = team_name
        self._version = version

    def str(self):
        return f"(init {self._team_name})"
