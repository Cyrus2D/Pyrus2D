from enum import Enum, unique, auto


class TrainerCommand:
    @unique
    class Type(Enum):
        INIT = auto()  # connection command

        CHECK_BALL = auto()
        LOOK = auto()
        TEAM_NAMES = auto()

        EAR = auto()
        EYE = auto()

        START = auto()
        CHANGE_MODE = auto()
        MOVE = auto()
        RECOVER = auto()
        CHANGE_PLAYER_TYPE = auto()
        SAY = auto()

        COMPRESSION = auto()
        DONE = auto()

        ILLEGAL = auto()

    def __init__(self):
        pass

    def type(self):
        pass

    def str(self):
        pass
