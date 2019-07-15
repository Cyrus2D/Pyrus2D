"""
  #file types.py
  #brief the type definition set for the RCSSServer2D

"""

from enum import Enum, unique, auto

"""
  \ enum SideID
  \ brief side type definition
"""


@unique
class SideID(Enum):
    LEFT = 'l'
    NEUTRAL = 'n'
    RIGHT = 'r'


"""
  \ enum MarkerID
  \ brief marker type definition
"""


class MarkerID(Enum):
    Goal_L = 1  # 1
    Goal_R = 1  # 1

    Flag_C = 2
    Flag_CT = 3
    Flag_CB = 4
    Flag_LT = 5
    Flag_LB = 6
    Flag_RT = 7
    Flag_RB = 8
    # 8

    Flag_PLT = 9
    Flag_PLC = 10
    Flag_PLB = 11
    Flag_PRT = 12
    Flag_PRC = 13
    Flag_PRB = 14
    # 14

    Flag_GLT = 15
    Flag_GLB = 16
    Flag_GRT = 17
    Flag_GRB = 18  # 18

    Flag_TL50 = 19
    Flag_TL40 = 20
    Flag_TL30 = 21
    Flag_TL20 = 22
    Flag_TL10 = 23  # 23
    Flag_T0 = 24

    Flag_TR10 = 25
    Flag_TR20 = 26
    Flag_TR30 = 27
    Flag_TR40 = 28
    Flag_TR50 = 29  # 29

    Flag_BL50 = 30
    Flag_BL40 = 31
    Flag_BL30 = 32
    Flag_BL20 = 33
    Flag_BL10 = 34
    Flag_B0 = 35

    Flag_BR10 = 36
    Flag_BR20 = 37
    Flag_BR30 = 38
    Flag_BR40 = 39
    Flag_BR50 = 40  # 40

    Flag_LT30 = 41
    Flag_LT20 = 42
    Flag_LT10 = 43  # 43
    Flag_L0 = 44

    Flag_LB10 = 45
    Flag_LB20 = 46
    Flag_LB30 = 47  # 47

    Flag_RT30 = 48
    Flag_RT20 = 49
    Flag_RT10 = 50  # 50
    Flag_R0 = 51

    Flag_RB10 = 52
    Flag_RB20 = 53
    Flag_RB30 = 54

    Marker_Unknown = 55


"""
  \ enum LineID
  \ brief line type definition
"""


@unique
class LineID(Enum):
    Line_Left = auto()
    Line_Right = auto()
    Line_Top = auto()
    Line_Bottom = auto()
    Line_Unknown = auto()


"""
  \ enum PlayMode
  \ brief play mode types defined in rcssserver/src/types.h
"""


@unique
class PlayMode(Enum):
    PM_Null = auto()
    PM_BeforeKickOff = auto()
    PM_TimeOver = auto()
    PM_PlayOn = auto()
    PM_KickOff_Left = auto()
    PM_KickOff_Right = auto()
    PM_KickIn_Left = auto()
    PM_KickIn_Right = auto()
    PM_FreeKick_Left = auto()
    PM_FreeKick_Right = auto()
    PM_CornerKick_Left = auto()
    PM_CornerKick_Right = auto()
    PM_GoalKick_Left = auto()
    PM_GoalKick_Right = auto()
    PM_AfterGoal_Left = auto()
    PM_AfterGoal_Right = auto()  # - sserver-2.94
    PM_Drop_Ball = auto()  # - sserver-3.29
    PM_OffSide_Left = auto()
    PM_OffSide_Right = auto()  # until sserver-5.27
    PM_PK_Left = auto()
    PM_PK_Right = auto()
    PM_FirstHalfOver = auto()
    PM_Pause = auto()
    PM_Human = auto()
    PM_Foul_Charge_Left = auto()
    PM_Foul_Charge_Right = auto()
    PM_Foul_Push_Left = auto()
    PM_Foul_Push_Right = auto()
    PM_Foul_MultipleAttacker_Left = auto()
    PM_Foul_MultipleAttacker_Right = auto()
    PM_Foul_BallOut_Left = auto()
    PM_Foul_BallOut_Right = auto()  # until sserver-7.11
    PM_Back_Pass_Left = auto()  # after rcssserver-8.05-rel
    PM_Back_Pass_Right = auto()
    PM_Free_Kick_Fault_Left = auto()
    PM_Free_Kick_Fault_Right = auto()
    PM_CatchFault_Left = auto()
    PM_CatchFault_Right = auto()
    PM_IndFreeKick_Left = auto()  # after rcssserver-9.2.0
    PM_IndFreeKick_Right = auto()
    PM_PenaltySetup_Left = auto()  # after rcssserver-9.3.0
    PM_PenaltySetup_Right = auto()
    PM_PenaltyReady_Left = auto()
    PM_PenaltyReady_Right = auto()
    PM_PenaltyTaken_Left = auto()
    PM_PenaltyTaken_Right = auto()
    PM_PenaltyMiss_Left = auto()
    PM_PenaltyMiss_Right = auto()
    PM_PenaltyScore_Left = auto()
    PM_PenaltyScore_Right = auto()
    PM_MAX = auto()


"""
    \enum BallStatus
    \ brief ball position status for coach/trainer
"""


@unique
class BallStatus(Enum):
    Ball_Null = auto()
    Ball_InField = auto()
    Ball_GoalL = auto()
    Ball_GoalR = auto()
    Ball_OutOfField = auto()
    Ball_MA = auto()


"""
  \enum Card
  \ brief card type
"""


@unique
class Card(Enum):
    YELLOW = auto()
    RED = auto()
    NO_CARD = auto()


"""
    some const variable

"""

# ! max player number in one team
MAX_PLAYER = 11

# ! uniform number that represents the unknown player
UNUM_UNKNOWN = -1

# ! Id of the unknown player type
HETERO_UNKNOWN = -1
# ! Id of the default player type
HETERO_DEFAULT = 0

# ! playmode string table defined in rcssserver.
PLAYMODE_STRINGS = ["",  # TODO Value of PlayerMode enum be these strings....?
                    "before_kick_off",
                    "time_over",
                    "play_on",
                    "kick_off_l",
                    "kick_off_r",
                    "kick_in_l",
                    "kick_in_r",
                    "free_kick_l",
                    "free_kick_r",
                    "corner_kick_l",
                    "corner_kick_r",
                    "goal_kick_l",
                    "goal_kick_r",
                    "goal_l",
                    "goal_r",
                    "drop_ball",
                    "offside_l",
                    "offside_r",
                    "penalty_kick_l",
                    "penalty_kick_r",
                    "first_half_over",
                    "pause",
                    "human_judge",
                    "foul_charge_l",
                    "foul_charge_r",
                    "foul_push_l",
                    "foul_push_r",
                    "foul_multiple_attack_l",
                    "foul_multiple_attack_r",
                    "foul_ballout_l",
                    "foul_ballout_r",
                    "back_pass_l",
                    "back_pass_r",
                    "free_kick_fault_l",
                    "free_kick_fault_r",
                    "catch_fault_l",
                    "catch_fault_r",
                    "indirect_free_kick_l",
                    "indirect_free_kick_r",
                    "penalty_setup_l",
                    "penalty_setup_r",
                    "penalty_ready_l",
                    "penalty_ready_r",
                    "penalty_taken_l",
                    "penalty_taken_r",
                    "penalty_miss_l",
                    "penalty_miss_r",
                    "penalty_score_l",
                    "penalty_score_r",
                    "",
                    "",
                    "",
                    "",
                    ""
                    ]

# available characters in player's say or coach's free form message
# [-0-9a-zA-Z ().+*/?<>_]
# 74 characters

# ! character set that player can say.
SAY_CHARACTERS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ().+*/?<>_-"

# ! ball status string table for trainer.
BALL_STATUS_STRINGS = ["",
                       "in_field",
                       "goal_l",
                       "goal_r",
                       "out_of_field",
                       ]
