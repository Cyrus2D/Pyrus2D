from lib.network.udp_socket import UDPSocket, IPAddress
from lib.parser import MessageRecieveParser
from lib.player_command.player_body_command import *
from lib.player_command.player_command import *


def main():
    udp = UDPSocket(IPAddress('127.0.0.1', 6000))
    udp.send_msg(PlayerInitCommand("Pyrus", 8).str())
    d, s = udp.recieve_msg()
    print(s[0], s[1])
    while True:
        udp2 = UDPSocket(IPAddress('127.0.0.1', s[1]))
        d, s = udp.recieve_msg()
        print(s, d)
        command = PlayerDashCommand(100, 90)
        udp2.send_msg(command.str())


if __name__ == "__main__":
    # main()
    # print("done")
    s = '(server_param (audio_cut_dist 50)(back_passes 1)(ball_accel_max 2.7)(ball_decay 0.94)(ball_rand 0.05)(ball_size 0.085)(ball_speed_max 3)(ball_weight 0.2)(catch_ban_cycle 5)(catch_probability 1)(catchable_area_l 1.2)(catchable_area_w 1)(ckick_margin 1)(clang_advice_win 1)(clang_define_win 1)(clang_del_win 1)(clang_info_win 1)(clang_mess_delay 50)(clang_mess_per_cycle 1)(clang_meta_win 1)(clang_rule_win 1)(clang_win_size 300)(coach 0)(coach_port 6001)(coach_w_referee 0)(control_radius 2)(dash_power_rate 0.006)(drop_ball_time 100)(effort_dec 0.005)(effort_dec_thr 0.3)(effort_inc 0.01)(effort_inc_thr 0.6)(effort_init 1)(effort_min 0.6)(forbid_kick_off_offside 1)(free_kick_faults 1)(freeform_send_period 20)(freeform_wait_period 600)(fullstate_l 1)(fullstate_r 1)(game_log_compression 0)(game_log_dated 1)(game_log_dir "./")(game_log_fixed 0)(game_log_fixed_name "rcssserver")(game_log_version 5)(game_logging 1)(goal_width 14.02)(goalie_max_moves 2)(half_time 300)(hear_decay 1)(hear_inc 1)(hear_max 1)(inertia_moment 5)(kick_power_rate 0.027)(kick_rand 0.1)(kick_rand_factor_l 1)(kick_rand_factor_r 1)(kickable_margin 0.7)(landmark_file "~/.rcssserver-landmark.xml")(log_date_format "%Y%m%d%H%M%S-")(log_times 0)(max_goal_kicks 3)(maxmoment 180)(maxneckang 90)(maxneckmoment 180)(maxpower 100)(minmoment -180)(minneckang -90)(minneckmoment -180)(minpower -100)(offside_active_area_size 2.5)(offside_kick_margin 9.15)(olcoach_port 6002)(old_coach_hear 0)(player_accel_max 1)(player_decay 0.4)(player_rand 0.1)(player_size 0.3)(player_speed_max 1.05)(player_weight 60)(point_to_ban 5)(point_to_duration 20)(port 6000)(prand_factor_l 1)(prand_factor_r 1)(profile 0)(proper_goal_kicks 0)(quantize_step 0.1)(quantize_step_l 0.01)(record_messages 0)(recover_dec 0.002)(recover_dec_thr 0.3)(recover_min 0.5)(recv_step 10)(say_coach_cnt_max 128)(say_coach_msg_size 128)(say_msg_size 10)(send_comms 0)(send_step 150)(send_vi_step 100)(sense_body_step 100)(simulator_step 100)(slow_down_factor 1)(slowness_on_top_for_left_team 1)(slowness_on_top_for_right_team 1)(stamina_inc_max 45)(stamina_max 8000)(start_goal_l 0)(start_goal_r 0)(stopped_ball_vel 0.01)(synch_micro_sleep 1)(synch_mode 1)(synch_offset 60)(tackle_back_dist 0)(tackle_cycles 10)(tackle_dist 2)(tackle_exponent 6)(tackle_power_rate 0.027)(tackle_width 1.25)(team_actuator_noise 0)(text_log_compression 0)(text_log_dated 1)(text_log_dir "./")(text_log_fixed 0)(text_log_fixed_name "rcssserver")(text_logging 1)(use_offside 1)(verbose 0)(visible_angle 90)(visible_distance 3)(wind_ang 0)(wind_dir 0)(wind_force 0)(wind_none 0)(wind_rand 0)(wind_random 0))'
    parser = MessageRecieveParser().parse(s)
    print(str(parser))
