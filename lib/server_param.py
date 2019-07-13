from lib.parser.parser_message_params import MessageParamsParser

DEFAULT_MAX_PLAYER = 11
DEFAULT_PITCH_LENGTH = 105.0
DEFAULT_PITCH_WIDTH = 68.0
DEFAULT_PITCH_MARGIN = 5.0
DEFAULT_CENTER_CIRCLE_R = 9.15
DEFAULT_PENALTY_AREA_LENGTH = 16.5
DEFAULT_PENALTY_AREA_WIDTH = 40.32
DEFAULT_PENALTY_CIRCLE_R = 9.15
DEFAULT_PENALTY_SPOT_DIST = 11.0
DEFAULT_GOAL_AREA_LENGTH = 5.5
DEFAULT_GOAL_AREA_WIDTH = 18.32
DEFAULT_GOAL_DEPTH = 2.44
DEFAULT_CORNER_ARC_R = 1.0
#  DEFAULT_KICK_OFF_CLEAR_DISTANCE = CENTER_CIRCLE_R
DEFAULT_GOAL_POST_RADIUS = 0.06

DEFAULT_WIND_WEIGHT = 10000.0

DEFAULT_GOAL_WIDTH = 14.02
DEFAULT_INERTIA_MOMENT = 5.0

DEFAULT_PLAYER_SIZE = 0.3
DEFAULT_PLAYER_DECAY = 0.4
DEFAULT_PLAYER_RAND = 0.05
DEFAULT_PLAYER_WEIGHT = 60.0
DEFAULT_PLAYER_SPEED_MAX = 1.2
DEFAULT_PLAYER_ACCEL_MAX = 1.0

DEFAULT_STAMINA_MAX = 4000.0
DEFAULT_STAMINA_INC_MAX = 45.0

DEFAULT_RECOVER_INIT = 1.0
DEFAULT_RECOVER_DEC_THR = 0.3
DEFAULT_RECOVER_MIN = 0.5
DEFAULT_RECOVER_DEC = 0.002

DEFAULT_EFFORT_INIT = 1.0
DEFAULT_EFFORT_DEC_THR = 0.3
DEFAULT_EFFORT_MIN = 0.6
DEFAULT_EFFORT_DEC = 0.005
DEFAULT_EFFORT_INC_THR = 0.6
DEFAULT_EFFORT_INC = 0.01

DEFAULT_KICK_RAND = 0.0
DEFAULT_TEAM_ACTUATOR_NOISE = False
DEFAULT_PLAYER_RAND_FACTOR_L = 1.0
DEFAULT_PLAYER_RAND_FACTOR_R = 1.0
DEFAULT_KICK_RAND_FACTOR_L = 1.0
DEFAULT_KICK_RAND_FACTOR_R = 1.0

DEFAULT_BALL_SIZE = 0.085
DEFAULT_BALL_DECAY = 0.94
DEFAULT_BALL_RAND = 0.05
DEFAULT_BALL_WEIGHT = 0.2
DEFAULT_BALL_SPEED_MAX = 2.7
DEFAULT_BALL_ACCEL_MAX = 2.7

DEFAULT_DASH_POWER_RATE = 0.006
DEFAULT_KICK_POWER_RATE = 0.027
DEFAULT_KICKABLE_MARGIN = 0.7
DEFAULT_CONTROL_RADIUS = 2.0
#  DEFAULT_CONTROL_RADIUS_WIDTH
# = DEFAULT_CONTROL_RADIUS - DEFAULT_PLAYER_SIZE

DEFAULT_MAX_POWER = 100.0
DEFAULT_MIN_POWER = -100.0
DEFAULT_MAX_MOMENT = 180.0
DEFAULT_MIN_MOMENT = -180.0
DEFAULT_MAX_NECK_MOMENT = 180.0
DEFAULT_MIN_NECK_MOMENT = -180.0
DEFAULT_MAX_NECK_ANGLE = 90.0
DEFAULT_MIN_NECK_ANGLE = -90.0

DEFAULT_VISIBLE_ANGLE = 90.0
DEFAULT_VISIBLE_DISTANCE = 3.0

DEFAULT_WIND_DIR = 0.0
DEFAULT_WIND_FORCE = 0.0
DEFAULT_WIND_ANGLE = 0.0
DEFAULT_WIND_RAND = 0.0

#  DEFAULT_KICKABLE_AREA
# = KICKABLE_MARGIN + PLAYER_SIZE + BALL_SIZE

DEFAULT_CATCH_AREA_L = 2.0
DEFAULT_CATCH_AREA_W = 1.0
DEFAULT_CATCH_PROBABILITY = 1.0
DEFAULT_GOALIE_MAX_MOVES = 2

DEFAULT_CORNER_KICK_MARGIN = 1.0
DEFAULT_OFFSIDE_ACTIVE_AREA_SIZE = 2.5

DEFAULT_WIND_NONE = False
DEFAULT_USE_WIND_RANDOM = False

DEFAULT_COACH_SAY_COUNT_MAX = 128
# defined as DEF_SAY_COACH_CNT_MAX
DEFAULT_COACH_SAY_MSG_SIZE = 128

DEFAULT_CLANG_WIN_SIZE = 300
DEFAULT_CLANG_DEFINE_WIN = 1
DEFAULT_CLANG_META_WIN = 1
DEFAULT_CLANG_ADVICE_WIN = 1
DEFAULT_CLANG_INFO_WIN = 1
DEFAULT_CLANG_MESS_DELAY = 50
DEFAULT_CLANG_MESS_PER_CYCLE = 1

DEFAULT_HALF_TIME = 300
DEFAULT_SIMULATOR_STEP = 100
DEFAULT_SEND_STEP = 150
DEFAULT_RECV_STEP = 10
DEFAULT_SENSE_BODY_STEP = 100
#    DEFAULT_LCM_STEP
# = lcm(sim_st, lcm(send_st, lcm(recv_st, lcm(sb_step, sv_st))))) of sync_offset

DEFAULT_PLAYER_SAY_MSG_SIZE = 10
DEFAULT_PLAYER_HEAR_MAX = 1
DEFAULT_PLAYER_HEAR_INC = 1
DEFAULT_PLAYER_HEAR_DECAY = 1

DEFAULT_CATCH_BAN_CYCLE = 5

DEFAULT_SLOW_DOWN_FACTOR = 1

DEFAULT_USE_OFFSIDE = True
DEFAULT_KICKOFF_OFFSIDE = True
DEFAULT_OFFSIDE_KICK_MARGIN = 9.15

DEFAULT_AUDIO_CUT_DIST = 50.0

DEFAULT_DIST_QUANTIZE_STEP = 0.1
DEFAULT_LANDMARK_DIST_QUANTIZE_STEP = 0.01
DEFAULT_DIR_QUANTIZE_STEP = 0.1
#  DEFAULT_DIST_QUANTIZE_STEP_L
#  DEFAULT_DIST_QUANTIZE_STEP_R
#  DEFAULT_LANDMARK_DIST_QUANTIZE_STEP_L
#  DEFAULT_LANDMARK_DIST_QUANTIZE_STEP_R
#  DEFAULT_DIR_QUANTIZE_STEP_L
#  DEFAULT_DIR_QUANTIZE_STEP_R

DEFAULT_COACH_MODE = False
DEFAULT_COACH_WITH_REFEREE_MODE = False
DEFAULT_USE_OLD_COACH_HEAR = False

DEFAULT_SLOWNESS_ON_TOP_FOR_LEFT_TEAM = 1.0
DEFAULT_SLOWNESS_ON_TOP_FOR_RIGHT_TEAM = 1.0

DEFAULT_START_GOAL_L = 0
DEFAULT_START_GOAL_R = 0

DEFAULT_FULLSTATE_L = False
DEFAULT_FULLSTATE_R = False

DEFAULT_DROP_BALL_TIME = 200

DEFAULT_SYNC_MODE = False
DEFAULT_SYNC_OFFSET = 60
DEFAULT_SYNC_MICRO_SLEEP = 1

DEFAULT_POINT_TO_BAN = 5
DEFAULT_POINT_TO_DURATION = 20

DEFAULT_PLAYER_PORT = 6000
DEFAULT_TRAINER_PORT = 6001
DEFAULT_ONLINE_COACH_PORT = 6002

DEFAULT_VERBOSE_MODE = False

DEFAULT_COACH_SEND_VI_STEP = 100

DEFAULT_REPLAY_FILE = ""  # unused after rcsserver-9+

DEFAULT_LANDMARK_FILE = "~/.rcssserver-landmark.xml"

DEFAULT_SEND_COMMS = False

DEFAULT_TEXT_LOGGING = True
DEFAULT_GAME_LOGGING = True
DEFAULT_GAME_LOG_VERSION = 3

DEFAULT_TEXT_LOG_DIR = "./"

DEFAULT_GAME_LOG_DIR = "./"

DEFAULT_TEXT_LOG_FIXED_NAME = "rcssserver"

DEFAULT_GAME_LOG_FIXED_NAME = "rcssserver"
DEFAULT_USE_TEXT_LOG_FIXED = False
DEFAULT_USE_GAME_LOG_FIXED = False
DEFAULT_USE_TEXT_LOG_DATED = True
DEFAULT_USE_GAME_LOG_DATED = True

DEFAULT_LOG_DATE_FORMAT = "%Y%m%d%H%M-"
DEFAULT_LOG_TIMES = False
DEFAULT_RECORD_MESSAGES = False
DEFAULT_TEXT_LOG_COMPRESSION = 0
DEFAULT_GAME_LOG_COMPRESSION = 0

DEFAULT_USE_PROFILE = False

DEFAULT_TACKLE_DIST = 2.0
DEFAULT_TACKLE_BACK_DIST = 0.5
DEFAULT_TACKLE_WIDTH = 1.0
DEFAULT_TACKLE_EXPONENT = 6.0
DEFAULT_TACKLE_CYCLES = 10
DEFAULT_TACKLE_POWER_RATE = 0.027

DEFAULT_FREEFORM_WAIT_PERIOD = 600
DEFAULT_FREEFORM_SEND_PERIOD = 20

DEFAULT_FREE_KICK_FAULTS = True
DEFAULT_BACK_PASSES = True

DEFAULT_PROPER_GOAL_KICKS = False
DEFAULT_STOPPED_BALL_VEL = 0.01
DEFAULT_MAX_GOAL_KICKS = 3

DEFAULT_CLANG_DEL_WIN = 1
DEFAULT_CLANG_RULE_WIN = 1

DEFAULT_AUTO_MODE = False
DEFAULT_KICK_OFF_WAIT = 100
DEFAULT_CONNECT_WAIT = 300
DEFAULT_GAME_OVER_WAIT = 100

DEFAULT_TEAM_L_START = ""

DEFAULT_TEAM_R_START = ""

DEFAULT_KEEPAWAY_MODE = False
# these value are defined in rcssserver/param.h
DEFAULT_KEEPAWAY_LENGTH = 20.0
DEFAULT_KEEPAWAY_WIDTH = 20.0

DEFAULT_KEEPAWAY_LOGGING = True

DEFAULT_KEEPAWAY_LOG_DIR = "./"

DEFAULT_KEEPAWAY_LOG_FIXED_NAME = "rcssserver"
DEFAULT_KEEPAWAY_LOG_FIXED = False
DEFAULT_KEEPAWAY_LOG_DATED = True

DEFAULT_KEEPAWAY_START = -1

DEFAULT_NR_NORMAL_HALFS = 2
DEFAULT_NR_EXTRA_HALFS = 2
DEFAULT_PENALTY_SHOOT_OUTS = True

DEFAULT_PEN_BEFORE_SETUP_WAIT = 30
DEFAULT_PEN_SETUP_WAIT = 100
DEFAULT_PEN_READY_WAIT = 50
DEFAULT_PEN_TAKEN_WAIT = 200
DEFAULT_PEN_NR_KICKS = 5
DEFAULT_PEN_MAX_EXTRA_KICKS = 10
DEFAULT_PEN_DIST_X = 42.5
DEFAULT_PEN_RANDOM_WINNER = False
DEFAULT_PEN_ALLOW_MULT_KICKS = True
DEFAULT_PEN_MAX_GOALIE_DIST_X = 14.0
DEFAULT_PEN_COACH_MOVES_PLAYERS = True

DEFAULT_MODULE_DIR = ""

DEFAULT_BALL_STUCK_AREA = 3.0

DEFAULT_MAX_TACKLE_POWER = 100.0
DEFAULT_MAX_BACK_TACKLE_POWER = 50.0
DEFAULT_PLAYER_SPEED_MAX_MIN = 0.8
DEFAULT_EXTRA_STAMINA = 0.0
DEFAULT_SYNCH_SEE_OFFSET = 30

EXTRA_HALF_TIME = 100

STAMINA_CAPACITY = -1.0  # 148600.0
MAX_DASH_ANGLE = 0.0  # 180.0
MIN_DASH_ANGLE = 0.0  # -180.0
DASH_ANGLE_STEP = 180.0  # 90.0
SIDE_DASH_RATE = 0.25
BACK_DASH_RATE = 0.5
MAX_DASH_POWER = 100.0
MIN_DASH_POWER = -100.0

# 14.0.0
TACKLE_RAND_FACTOR = 2.0
FOUL_DETECT_PROBABILITY = 0.5
FOUL_EXPONENT = 10.0
FOUL_CYCLES = 5


class ServerParam:  # TODO spicfic TYPES and change them
    def __init__(self):
        self._goal_width = DEFAULT_GOAL_WIDTH
        self._inertia_moment = DEFAULT_INERTIA_MOMENT

        self._player_size = DEFAULT_PLAYER_SIZE
        self._player_decay = DEFAULT_PLAYER_DECAY
        self._player_rand = DEFAULT_PLAYER_RAND
        self._player_weight = DEFAULT_PLAYER_WEIGHT
        self._player_speed_max = DEFAULT_PLAYER_SPEED_MAX
        self._player_accel_max = DEFAULT_PLAYER_ACCEL_MAX

        self._stamina_max = DEFAULT_STAMINA_MAX
        self._stamina_inc_max = DEFAULT_STAMINA_INC_MAX

        self._recover_init = DEFAULT_RECOVER_INIT
        self._recover_dec_thr = DEFAULT_RECOVER_DEC_THR
        self._recover_min = DEFAULT_RECOVER_MIN
        self._recover_dec = DEFAULT_RECOVER_DEC

        self._effort_init = DEFAULT_EFFORT_INIT
        self._effort_dec_thr = DEFAULT_EFFORT_DEC_THR
        self._effort_min = DEFAULT_EFFORT_MIN
        self._effort_dec = DEFAULT_EFFORT_DEC
        self._effort_inc_thr = DEFAULT_EFFORT_INC_THR
        self._effort_inc = DEFAULT_EFFORT_INC

        self._kick_rand = DEFAULT_KICK_RAND
        self._team_actuator_noise = DEFAULT_TEAM_ACTUATOR_NOISE
        self._player_rand_factor_l = DEFAULT_PLAYER_RAND_FACTOR_L
        self._player_rand_factor_r = DEFAULT_PLAYER_RAND_FACTOR_R
        self._kick_rand_factor_l = DEFAULT_KICK_RAND_FACTOR_L
        self._kick_rand_factor_r = DEFAULT_KICK_RAND_FACTOR_R

        self._ball_size = DEFAULT_BALL_SIZE
        self._ball_decay = DEFAULT_BALL_DECAY
        self._ball_rand = DEFAULT_BALL_RAND
        self._ball_weight = DEFAULT_BALL_WEIGHT
        self._ball_speed_max = DEFAULT_BALL_SPEED_MAX
        self._ball_accel_max = DEFAULT_BALL_ACCEL_MAX

        self._dash_power_rate = DEFAULT_DASH_POWER_RATE
        self._kick_power_rate = DEFAULT_KICK_POWER_RATE
        self._kickable_margin = DEFAULT_KICKABLE_MARGIN
        self._control_radius = DEFAULT_CONTROL_RADIUS
        self._control_radius_width = DEFAULT_CONTROL_RADIUS - DEFAULT_PLAYER_SIZE

        self._max_power = DEFAULT_MAX_POWER
        self._min_power = DEFAULT_MIN_POWER
        self._max_moment = DEFAULT_MAX_MOMENT
        self._min_moment = DEFAULT_MIN_MOMENT
        self._max_neck_moment = DEFAULT_MAX_NECK_MOMENT
        self._min_neck_moment = DEFAULT_MIN_NECK_MOMENT
        self._max_neck_angle = DEFAULT_MAX_NECK_ANGLE
        self._min_neck_angle = DEFAULT_MIN_NECK_ANGLE

        self._visible_angle = DEFAULT_VISIBLE_ANGLE
        self._visible_distance = DEFAULT_VISIBLE_DISTANCE

        self._wind_dir = DEFAULT_WIND_DIR
        self._wind_force = DEFAULT_WIND_FORCE
        self._wind_angle = DEFAULT_WIND_ANGLE
        self._wind_rand = DEFAULT_WIND_RAND

        self._kickable_area = DEFAULT_PLAYER_SIZE + DEFAULT_KICKABLE_MARGIN + DEFAULT_BALL_SIZE

        self._catch_area_l = DEFAULT_CATCH_AREA_L
        self._catch_area_w = DEFAULT_CATCH_AREA_W
        self._catch_probability = DEFAULT_CATCH_PROBABILITY
        self._goalie_max_moves = DEFAULT_GOALIE_MAX_MOVES

        self._corner_kick_margin = DEFAULT_CORNER_KICK_MARGIN
        self._offside_active_area_size = DEFAULT_OFFSIDE_ACTIVE_AREA_SIZE

        self._wind_none = DEFAULT_WIND_NONE
        self._use_wind_random = DEFAULT_USE_WIND_RANDOM

        self._coach_say_count_max = DEFAULT_COACH_SAY_COUNT_MAX
        self._coach_say_msg_size = DEFAULT_COACH_SAY_MSG_SIZE

        self._clang_win_size = DEFAULT_CLANG_WIN_SIZE
        self._clang_define_win = DEFAULT_CLANG_DEFINE_WIN
        self._clang_meta_win = DEFAULT_CLANG_META_WIN
        self._clang_advice_win = DEFAULT_CLANG_ADVICE_WIN
        self._clang_info_win = DEFAULT_CLANG_INFO_WIN
        self._clang_mess_delay = DEFAULT_CLANG_MESS_DELAY
        self._clang_mess_per_cycle = DEFAULT_CLANG_MESS_PER_CYCLE

        self._half_time = DEFAULT_HALF_TIME
        self._simulator_step = DEFAULT_SIMULATOR_STEP
        self._send_step = DEFAULT_SEND_STEP
        self._recv_step = DEFAULT_RECV_STEP
        self._sense_body_step = DEFAULT_SENSE_BODY_STEP
        self._lcm_step = 300  # lcm(simulator_step, send_step, recv_step, sense_body_step, send_vi_step)

        self._player_say_msg_size = DEFAULT_PLAYER_SAY_MSG_SIZE
        self._player_hear_max = DEFAULT_PLAYER_HEAR_MAX
        self._player_hear_inc = DEFAULT_PLAYER_HEAR_INC
        self._player_hear_decay = DEFAULT_PLAYER_HEAR_DECAY

        self._catch_ban_cycle = DEFAULT_CATCH_BAN_CYCLE

        self._slow_down_factor = DEFAULT_SLOW_DOWN_FACTOR

        self._use_offside = DEFAULT_USE_OFFSIDE
        self._kickoff_offside = DEFAULT_KICKOFF_OFFSIDE
        self._offside_kick_margin = DEFAULT_OFFSIDE_KICK_MARGIN

        self._audio_cut_dist = DEFAULT_AUDIO_CUT_DIST

        self._dist_quantize_step = DEFAULT_DIST_QUANTIZE_STEP
        self._landmark_dist_quantize_step = DEFAULT_LANDMARK_DIST_QUANTIZE_STEP
        self._dir_quantize_step = DEFAULT_DIR_QUANTIZE_STEP
        self._dist_quantize_step_l = DEFAULT_DIST_QUANTIZE_STEP
        self._dist_quantize_step_r = DEFAULT_DIST_QUANTIZE_STEP
        self._landmark_dist_quantize_step_l = DEFAULT_LANDMARK_DIST_QUANTIZE_STEP
        self._landmark_dist_quantize_step_r = DEFAULT_LANDMARK_DIST_QUANTIZE_STEP
        self._dir_quantize_step_l = DEFAULT_DIR_QUANTIZE_STEP
        self._dir_quantize_step_r = DEFAULT_DIR_QUANTIZE_STEP

        self._coach_mode = DEFAULT_COACH_MODE
        self._coach_with_referee_mode = DEFAULT_COACH_WITH_REFEREE_MODE
        self._use_old_coach_hear = DEFAULT_USE_OLD_COACH_HEAR

        self._slowness_on_top_for_left_team = DEFAULT_SLOWNESS_ON_TOP_FOR_LEFT_TEAM
        self._slowness_on_top_for_right_team = DEFAULT_SLOWNESS_ON_TOP_FOR_RIGHT_TEAM

        self._start_goal_l = DEFAULT_START_GOAL_L
        self._start_goal_r = DEFAULT_START_GOAL_R

        self._fullstate_l = DEFAULT_FULLSTATE_L
        self._fullstate_r = DEFAULT_FULLSTATE_R

        self._drop_ball_time = DEFAULT_DROP_BALL_TIME

        self._synch_mode = DEFAULT_SYNC_MODE
        self._synch_offset = DEFAULT_SYNC_OFFSET
        self._synch_micro_sleep = DEFAULT_SYNC_MICRO_SLEEP

        self._point_to_ban = DEFAULT_POINT_TO_BAN
        self._point_to_duration = DEFAULT_POINT_TO_DURATION

        # not defined in server_param_t
        self._player_port = DEFAULT_PLAYER_PORT
        self._trainer_port = DEFAULT_TRAINER_PORT
        self._online_coach_port = DEFAULT_ONLINE_COACH_PORT

        self._verbose_mode = DEFAULT_VERBOSE_MODE

        self._coach_send_vi_step = DEFAULT_COACH_SEND_VI_STEP

        self._replay_file = DEFAULT_REPLAY_FILE
        self._landmark_file = DEFAULT_LANDMARK_FILE

        self._send_comms = DEFAULT_SEND_COMMS

        self._text_logging = DEFAULT_TEXT_LOGGING
        self._game_logging = DEFAULT_GAME_LOGGING
        self._game_log_version = DEFAULT_GAME_LOG_VERSION
        self._text_log_dir = DEFAULT_TEXT_LOG_DIR
        self._game_log_dir = DEFAULT_GAME_LOG_DIR
        self._text_log_fixed_name = DEFAULT_TEXT_LOG_FIXED_NAME
        self._game_log_fixed_name = DEFAULT_GAME_LOG_FIXED_NAME
        self._use_text_log_fixed = DEFAULT_USE_TEXT_LOG_FIXED
        self._use_game_log_fixed = DEFAULT_USE_GAME_LOG_FIXED
        self._use_text_log_dated = DEFAULT_USE_TEXT_LOG_DATED
        self._use_game_log_dated = DEFAULT_USE_GAME_LOG_DATED
        self._log_date_format = DEFAULT_LOG_DATE_FORMAT
        self._log_times = DEFAULT_LOG_TIMES
        self._record_message = DEFAULT_RECORD_MESSAGES
        self._text_log_compression = DEFAULT_TEXT_LOG_COMPRESSION
        self._game_log_compression = DEFAULT_GAME_LOG_COMPRESSION

        self._use_profile = DEFAULT_USE_PROFILE

        self._tackle_dist = DEFAULT_TACKLE_DIST
        self._tackle_back_dist = DEFAULT_TACKLE_BACK_DIST
        self._tackle_width = DEFAULT_TACKLE_WIDTH
        self._tackle_exponent = DEFAULT_TACKLE_EXPONENT
        self._tackle_cycles = DEFAULT_TACKLE_CYCLES
        self._tackle_power_rate = DEFAULT_TACKLE_POWER_RATE

        self._freeform_wait_period = DEFAULT_FREEFORM_WAIT_PERIOD
        self._freeform_send_period = DEFAULT_FREEFORM_SEND_PERIOD

        self._free_kick_faults = DEFAULT_FREE_KICK_FAULTS
        self._back_passes = DEFAULT_BACK_PASSES

        self._proper_goal_kicks = DEFAULT_PROPER_GOAL_KICKS
        self._stopped_ball_vel = DEFAULT_STOPPED_BALL_VEL
        self._max_goal_kicks = DEFAULT_MAX_GOAL_KICKS

        self._clang_del_win = DEFAULT_CLANG_DEL_WIN
        self._clang_rule_win = DEFAULT_CLANG_RULE_WIN

        self._auto_mode = DEFAULT_AUTO_MODE
        self._kick_off_wait = DEFAULT_KICK_OFF_WAIT
        self._connect_wait = DEFAULT_CONNECT_WAIT
        self._game_over_wait = DEFAULT_GAME_OVER_WAIT
        self._team_l_start = DEFAULT_TEAM_L_START
        self._team_r_start = DEFAULT_TEAM_R_START

        self._keepaway_mode = DEFAULT_KEEPAWAY_MODE
        self._keepaway_length = DEFAULT_KEEPAWAY_LENGTH
        self._keepaway_width = DEFAULT_KEEPAWAY_WIDTH

        self._keepaway_logging = DEFAULT_KEEPAWAY_LOGGING
        self._keepaway_log_dir = DEFAULT_KEEPAWAY_LOG_DIR
        self._keepaway_log_fixed_name = DEFAULT_KEEPAWAY_LOG_FIXED_NAME
        self._keepaway_log_fixed = DEFAULT_KEEPAWAY_LOG_FIXED
        self._keepaway_log_dated = DEFAULT_KEEPAWAY_LOG_DATED

        self._keepaway_start = DEFAULT_KEEPAWAY_START

        self._nr_normal_halfs = DEFAULT_NR_NORMAL_HALFS
        self._nr_extra_halfs = DEFAULT_NR_EXTRA_HALFS
        self._penalty_shoot_outs = DEFAULT_PENALTY_SHOOT_OUTS

        self._pen_before_setup_wait = DEFAULT_PEN_BEFORE_SETUP_WAIT
        self._pen_setup_wait = DEFAULT_PEN_SETUP_WAIT
        self._pen_ready_wait = DEFAULT_PEN_READY_WAIT
        self._pen_taken_wait = DEFAULT_PEN_TAKEN_WAIT
        self._pen_nr_kicks = DEFAULT_PEN_NR_KICKS
        self._pen_max_extra_kicks = DEFAULT_PEN_MAX_EXTRA_KICKS
        self._pen_dist_x = DEFAULT_PEN_DIST_X
        self._pen_random_winner = DEFAULT_PEN_RANDOM_WINNER
        self._pen_allow_mult_kicks = DEFAULT_PEN_ALLOW_MULT_KICKS
        self._pen_max_goalie_dist_x = DEFAULT_PEN_MAX_GOALIE_DIST_X
        self._pen_coach_moves_players = DEFAULT_PEN_COACH_MOVES_PLAYERS

        self._module_dir = DEFAULT_MODULE_DIR

        # 11.0.0
        self._ball_stuck_area = DEFAULT_BALL_STUCK_AREA
        # self._coach_msg_file = ""

        # 12.0.0
        self._max_tackle_power = DEFAULT_MAX_TACKLE_POWER
        self._max_back_tackle_power = DEFAULT_MAX_BACK_TACKLE_POWER
        self._player_speed_max_min = DEFAULT_PLAYER_SPEED_MAX_MIN
        self._extra_stamina = DEFAULT_EXTRA_STAMINA
        self._synch_see_offset = DEFAULT_SYNCH_SEE_OFFSET

        self._max_monitors = -1

        # 12.1.3
        self._extra_half_time = EXTRA_HALF_TIME

        # 13.0.0
        self._stamina_capacity = STAMINA_CAPACITY
        self._max_dash_angle = MAX_DASH_ANGLE
        self._min_dash_angle = MIN_DASH_ANGLE
        self._dash_angle_step = DASH_ANGLE_STEP
        self._side_dash_rate = SIDE_DASH_RATE
        self._back_dash_rate = BACK_DASH_RATE
        self._max_dash_power = MAX_DASH_POWER
        self._min_dash_power = MIN_DASH_POWER

        # 14.0.0
        self._tackle_rand_factor = TACKLE_RAND_FACTOR
        self._foul_detect_probability = FOUL_DETECT_PROBABILITY
        self._foul_exponent = FOUL_EXPONENT
        self._foul_cycles = FOUL_CYCLES
        self._random_seed = -1
        self._golden_goal = True

    def set_data(self, dic):
        self._audio_cut_dist = dic["audio_cut_dist"]
        self._back_passes = dic["back_passes"]
        self._ball_accel_max = dic["ball_accel_max"]
        self._ball_decay = dic["ball_decay"]
        self._ball_rand = dic["ball_rand"]
        self._ball_size = dic["ball_size"]
        self._ball_speed_max = dic["ball_speed_max"]
        self._ball_weight = dic["ball_weight"]
        self._catch_ban_cycle = dic["catch_ban_cycle"]
        self._catch_probability = dic["catch_probability"]
        self._catch_area_l = dic["catchable_area_l"]
        self._catch_area_w = dic["catchable_area_w"]
        self._corner_kick_margin = dic["ckick_margin"]
        self._clang_advice_win = dic["clang_advice_win"]
        self._clang_define_win = dic["clang_define_win"]
        self._clang_del_win = dic["clang_del_win"]
        self._clang_info_win = dic["clang_info_win"]
        self._clang_mess_delay = dic["clang_mess_delay"]
        self._clang_mess_per_cycle = dic["clang_mess_per_cycle"]
        self._clang_meta_win = dic["clang_meta_win"]
        self._clang_rule_win = dic["clang_rule_win"]
        self._clang_win_size = dic["clang_win_size"]
        self._coach_mode = dic["coach"]
        self._trainer_port = dic["coach_port"]
        self._coach_with_referee_mode = dic["coach_w_referee"]
        self._control_radius = dic["control_radius"]
        self._dash_power_rate = dic["dash_power_rate"]
        self._drop_ball_time = dic["drop_ball_time"]
        self._effort_dec = dic["effort_dec"]
        self._effort_dec_thr = dic["effort_dec_thr"]
        self._effort_inc = dic["effort_inc"]
        self._effort_inc_thr = dic["effort_inc_thr"]
        self._effort_init = dic["effort_init"]
        self._effort_min = dic["effort_min"]
        self._kickoff_offside = dic["forbid_kick_off_offside"]
        self._free_kick_faults = dic["free_kick_faults"]
        self._freeform_send_period = dic["freeform_send_period"]
        self._freeform_wait_period = dic["freeform_wait_period"]
        self._fullstate_l = dic["fullstate_l"]
        self._fullstate_r = dic["fullstate_r"]
        self._game_log_compression = dic["game_log_compression"]
        self._use_game_log_dated = dic["game_log_dated"]
        self._game_log_dir = dic["game_log_dir"]
        self._use_game_log_fixed = dic["game_log_fixed"]
        self._game_log_fixed_name = dic["game_log_fixed_name"]
        self._game_log_version = dic["game_log_version"]
        self._game_logging = dic["game_logging"]
        self._goal_width = dic["goal_width"]
        self._goalie_max_moves = dic["goalie_max_moves"]
        self._half_time = dic["half_time"]
        self._player_hear_decay = dic["hear_decay"]
        self._player_hear_inc = dic["hear_inc"]
        self._player_hear_max = dic["hear_max"]
        self._inertia_moment = dic["inertia_moment"]
        self._kick_power_rate = dic["kick_power_rate"]
        self._kick_rand = dic["kick_rand"]
        self._kick_rand_factor_l = dic["kick_rand_factor_l"]
        self._kick_rand_factor_r = dic["kick_rand_factor_r"]
        self._kickable_margin = dic["kickable_margin"]
        self._landmark_file = dic["landmark_file"]
        self._log_date_format = dic["log_date_format"]
        self._log_times = dic["log_times"]
        self._max_goal_kicks = dic["max_goal_kicks"]
        self._max_moment = dic["maxmoment"]
        self._max_neck_angle = dic["maxneckang"]
        self._max_neck_moment = dic["maxneckmoment"]
        self._max_power = dic["maxpower"]
        self._min_moment = dic["minmoment"]
        self._min_neck_angle = dic["minneckang"]
        self._min_neck_moment = dic["minneckmoment"]
        self._min_power = dic["minpower"]
        self._offside_active_area_size = dic["offside_active_area_size"]
        self._offside_kick_margin = dic["offside_kick_margin"]
        self._online_coach_port = dic["olcoach_port"]
        self._use_old_coach_hear = dic["old_coach_hear"]
        self._player_accel_max = dic["player_accel_max"]
        self._player_decay = dic["player_decay"]
        self._player_rand = dic["player_rand"]
        self._player_size = dic["player_size"]
        self._player_speed_max = dic["player_speed_max"]
        self._player_weight = dic["player_weight"]
        self._point_to_ban = dic["point_to_ban"]
        self._point_to_duration = dic["point_to_duration"]
        self._player_port = dic["port"]
        self._player_rand_factor_l = dic["prand_factor_l"]
        self._player_rand_factor_r = dic["prand_factor_r"]
        self._use_profile = dic["profile"]
        self._proper_goal_kicks = dic["proper_goal_kicks"]
        self._dist_quantize_step = dic["quantize_step"]
        self._dist_quantize_step_l = dic["quantize_step_l"]
        self._record_message = dic["record_messages"]
        self._recover_dec = dic["recover_dec"]
        self._recover_dec_thr = dic["recover_dec_thr"]
        self._recover_min = dic["recover_min"]
        self._recv_step = dic["recv_step"]
        self._coach_say_count_max = dic["say_coach_cnt_max"]
        self._coach_say_msg_size = dic["say_coach_msg_size"]
        self._player_say_msg_size = dic["say_msg_size"]
        self._send_comms = dic["send_comms"]
        self._send_step = dic["send_step"]
        self._coach_send_vi_step = dic["send_vi_step"]
        self._sense_body_step = dic["sense_body_step"]
        self._simulator_step = dic["simulator_step"]
        self._slow_down_factor = dic["slow_down_factor"]
        self._slowness_on_top_for_left_team = dic["slowness_on_top_for_left_team"]
        self._slowness_on_top_for_right_team = dic["slowness_on_top_for_right_team"]
        self._stamina_inc_max = dic["stamina_inc_max"]
        self._stamina_max = dic["stamina_max"]
        self._start_goal_l = dic["start_goal_l"]
        self._start_goal_r = dic["start_goal_r"]
        self._stopped_ball_vel = dic["stopped_ball_vel"]
        self._synch_micro_sleep = dic["synch_micro_sleep"]
        self._synch_mode = dic["synch_mode"]
        self._synch_offset = dic["synch_offset"]
        self._tackle_back_dist = dic["tackle_back_dist"]
        self._tackle_cycles = dic["tackle_cycles"]
        self._tackle_dist = dic["tackle_dist"]
        self._tackle_exponent = dic["tackle_exponent"]
        self._tackle_power_rate = dic["tackle_power_rate"]
        self._tackle_width = dic["tackle_width"]
        self._team_actuator_noise = dic["team_actuator_noise"]
        self._text_log_compression = dic["text_log_compression"]
        self._use_text_log_dated = dic["text_log_dated"]
        self._text_log_dir = dic["text_log_dir"]
        self._use_text_log_fixed = dic["text_log_fixed"]
        self._text_log_fixed_name = dic["text_log_fixed_name"]
        self._text_logging = dic["text_logging"]
        self._use_offside = dic["use_offside"]
        self._verbose_mode = dic["verbose"]
        self._visible_angle = dic["visible_angle"]
        self._visible_distance = dic["visible_distance"]
        self._wind_angle = dic["wind_ang"]
        self._wind_dir = dic["wind_dir"]
        self._wind_force = dic["wind_force"]
        self._wind_none = dic["wind_none"]
        self._wind_rand = dic["wind_rand"]
        self._use_wind_random = dic["wind_random"]

    def parse(self, message):
        dic = MessageParamsParser().parse(message)
        self.set_data(dic['server_param'])
