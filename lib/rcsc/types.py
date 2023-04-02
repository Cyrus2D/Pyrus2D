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
    
    def invert(self):
        return SideID.RIGHT if self == SideID.LEFT else SideID.LEFT if self != SideID.NEUTRAL else SideID.NEUTRAL

    def __repr__(self):
        return self.value


"""
  \ enum MarkerID
  \ brief marker type definition
"""


class MarkerID(Enum):
    Goal_L = 0  # 1
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
    Line_Left = 'l'
    Line_Right = 'r'
    Line_Top = 't'
    Line_Bottom = 'b'
    Line_Unknown = auto()


"""
  \ enum GameModeType
  \ brief play mode types defined in rcssserver/src/types.h
"""


@unique
class GameModeType(Enum):
    Null = "null"
    BeforeKickOff = "before_kick_off"
    TimeOver = "time_over"
    PlayOn = "play_on"
    KickOff_Left = "kick_off_l"
    KickOff_Right = "kick_off_r"
    KickIn_Left = "kick_in_l"
    KickIn_Right = "kick_in_r"
    FreeKick_Left = "free_kick_l"
    FreeKick_Right = "free_kick_r"
    CornerKick_Left = "corner_kick_l"
    CornerKick_Right = "corner_kick_r"
    GoalKick_Left = "goal_kick_l"
    GoalKick_Right = "goal_kick_r"
    AfterGoal_Left = "goal_l"
    AfterGoal_Right = "goal_r"  # - sserver-2.94
    Drop_Ball = "drop_ball"  # - sserver-3.29
    OffSide_Left = "offside_l"
    OffSide_Right = "offside_r"  # until sserver-5.27
    PK_Left = "penalty_kick_l"
    PK_Right = "penalty_kick_r"
    FirstHalfOver = "first_half_over"
    Pause = "pause"
    Human = "human_judge"
    Foul_Charge_Left = "foul_charge_l"
    Foul_Charge_Right = "foul_charge_r"
    Foul_Push_Left = "foul_push_l"
    Foul_Push_Right = "foul_push_r"
    Foul_MultipleAttacker_Left = "foul_multiple_attack_l"
    Foul_MultipleAttacker_Right = "foul_multiple_attack_r"
    Foul_BallOut_Left = "foul_ballout_l"
    Foul_BallOut_Right = "foul_ballout_r"  # until sserver-7.11
    Back_Pass_Left = "back_pass_l"  # after rcssserver-8.05-rel
    Back_Pass_Right = "back_pass_r"
    Free_Kick_Fault_Left = "free_kick_fault_l"
    Free_Kick_Fault_Right = "free_kick_fault_r"
    CatchFault_Left = "catch_fault_l"
    CatchFault_Right = "catch_fault_r"
    IndFreeKick_Left = "indirect_free_kick_l"  # after rcssserver-9.2.0
    IndFreeKick_Right = "indirect_free_kick_r"
    PenaltySetup_Left = "penalty_setup_l"  # after rcssserver-9.3.0
    PenaltySetup_Right = "penalty_setup_r"
    PenaltyReady_Left = "penalty_ready_l"
    PenaltyReady_Right = "penalty_ready_r"
    PenaltyTaken_Left = "penalty_taken_l"
    PenaltyTaken_Right = "penalty_taken_r"
    PenaltyMiss_Left = "penalty_miss_l"
    PenaltyMiss_Right = "penalty_miss_r"
    PenaltyScore_Left = "penalty_score_l"
    PenaltyScore_Right = "penalty_score_r"
    GoalieCatchBall_Left = "goalie_catch_ball_l"
    GoalieCatchBall_Right = "goalie_catch_ball_r"
    IllegalDefense_Left = "illegal_defense_l"
    IllegalDefense_Right = "illegal_defense_r"
    HalfTime = "half_time"
    MAX = "max"

    def is_kick_off(self):
        return self == GameModeType.KickOff_Left or self == GameModeType.KickOff_Right

    def is_kick_in(self):
        return self == GameModeType.KickIn_Left or self == GameModeType.KickIn_Right

    def is_free_kick(self):
        return self == GameModeType.FreeKick_Left or self == GameModeType.FreeKick_Right

    def is_corner_kick(self):
        return self == GameModeType.CornerKick_Left or self == GameModeType.CornerKick_Right

    def is_goal_kick(self):
        return self == GameModeType.GoalKick_Left or self == GameModeType.GoalKick_Right

    def is_after_goal(self):
        return self == GameModeType.AfterGoal_Left or self == GameModeType.AfterGoal_Right

    def is_offside(self):
        return self == GameModeType.OffSide_Left or self == GameModeType.OffSide_Right

    def is_pk(self):
        return self == GameModeType.PK_Left or self == GameModeType.PK_Right

    def is_foul_charge(self):
        return self == GameModeType.Foul_Charge_Left or self == GameModeType.Foul_Charge_Right

    def is_foul_push(self):
        return self == GameModeType.Foul_Push_Left or self == GameModeType.Foul_Push_Right

    def is_foul_multiple_attacker(self):
        return self == GameModeType.Foul_MultipleAttacker_Left or self == GameModeType.Foul_MultipleAttacker_Right

    def is_foul_ball_out(self):
        return self == GameModeType.Foul_BallOut_Left or self == GameModeType.Foul_BallOut_Right

    def is_back_pass(self):
        return self == GameModeType.Back_Pass_Left or self == GameModeType.Back_Pass_Right

    def is_free_kick_fault(self):
        return self == GameModeType.Free_Kick_Fault_Left or self == GameModeType.Free_Kick_Fault_Right

    def is_catch_fault(self):
        return self == GameModeType.CatchFault_Left or self == GameModeType.CatchFault_Right

    def is_ind_free_kick(self):
        return self == GameModeType.IndFreeKick_Left or self == GameModeType.IndFreeKick_Right

    def is_penalty_setup(self):
        return self == GameModeType.PenaltySetup_Left or self == GameModeType.PenaltySetup_Right

    def is_penalty_ready(self):
        return self == GameModeType.PenaltyReady_Left or self == GameModeType.PenaltyReady_Right

    def is_penalty_taken(self):
        return self == GameModeType.PenaltyTaken_Left or self == GameModeType.PenaltyTaken_Right

    def is_penalty_miss(self):
        return self == GameModeType.PenaltyMiss_Left or self == GameModeType.PenaltyMiss_Right

    def is_penalty_score(self):
        return self == GameModeType.PenaltyScore_Left or self == GameModeType.PenaltyScore_Right

    def is_goalie_catch_ball(self):
        return self == GameModeType.GoalieCatchBall_Left or self == GameModeType.GoalieCatchBall_Right

    def is_illegal_defense(self):
        return self == GameModeType.IllegalDefense_Left or self == GameModeType.IllegalDefense_Right
    
    def side(self) -> SideID:
        side = self.value.split('_')[-1]
        if side == "l":
            return SideID.LEFT
        if side == "r":
            return SideID.RIGHT
        return SideID.NEUTRAL


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
GAMEMODETYPE_STRINGS = ["",  # TODO Value of PlayerMode enum be these strings....?
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
                        "illegal_defense_l",
                        "illegal_defense_r",
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


@unique
class ViewWidth(Enum):
    NARROW = 'narrow'
    NORMAL = 'normal'
    WIDE = 'wide'
    ILLEGAL = 'illegal'

    def __repr__(self):
        return self.value
    
    def width(self):
        if self is ViewWidth.NARROW:
            return 60.
        if self is ViewWidth.NORMAL:
            return 120.
        if self is ViewWidth.WIDE:
            return 180.
        return 0.

        
