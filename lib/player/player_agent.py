from typing import Union
import logging
import time

from lib.action.kick_table import KickTable
from base.decision import get_decision
from lib.debug.level import Level
from lib.debug.color import Color
from lib.debug.logger import dlog
from pyrusgeom.angle_deg import AngleDeg
from lib.player.action_effector import ActionEffector
from lib.player.sensor.body_sensor import BodySensor
from lib.player.sensor.see_state import SeeState
from lib.player.sensor.visual_sensor import VisualSensor
from lib.player.soccer_action import ViewAction, NeckAction, FocusPointAction
from lib.player.soccer_agent import SoccerAgent
from lib.player.world_model import WorldModel
from lib.network.udp_socket import IPAddress
from pyrusgeom.soccer_math import min_max
from lib.player_command.player_command import PlayerInitCommand, PlayerByeCommand
from lib.player_command.player_command_support import PlayerDoneCommand, PlayerTurnNeckCommand
from lib.player_command.player_command_sender import PlayerSendCommands
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.player.debug_client import DebugClient
from lib.rcsc.types import UNUM_UNKNOWN, GameModeType, SideID, ViewWidth
from lib.debug.debug_print import debug_print
from lib.messenger.messenger import Messenger

import team_config

def get_time_msec():
    return int(time.time()*1000)

class PlayerAgent(SoccerAgent):
    class Impl:
        def __init__(self, agent):
            self._agent: PlayerAgent = agent
            self._think_received = False
            self._current_time: GameTime = GameTime()
            self._last_decision_time: GameTime = GameTime()

            self._body = BodySensor()

            self._visual: VisualSensor = VisualSensor()
            self._see_state: SeeState = SeeState()
            self._team_name = team_config.TEAM_NAME

            self._game_mode: GameMode = GameMode()
            super().__init__()
            self._server_cycle_stopped: bool = True

            self._body_time_stamp:int = None

            dlog._time = self._current_time

            self._neck_action: NeckAction = None
            self._view_action: ViewAction = None
            self._focus_point_action: FocusPointAction = None

            self._goalie: bool = False

        def send_init_command(self):
            # TODO check reconnection

            com = PlayerInitCommand(team_config.TEAM_NAME, team_config.PLAYER_VERSION, self._goalie)
            # TODO set team name from config
            self._agent._full_world._team_name = team_config.TEAM_NAME

            if self._agent._client.send_message(com.str()) <= 0:
                debug_print("ERROR failed to connect to server")
                self._agent._client.set_server_alive(False)

        def send_bye_command(self):
            if self._agent._client.is_server_alive() is True: # TODO FALSE?
                com = PlayerByeCommand()
                self._agent._client.send_message(com.str())
                self._agent._client.set_server_alive(False)

        def sense_body_parser(self, message: str):
            self._body_time_stamp = get_time_msec()

            self.parse_cycle_info(message, True)

            dlog.add_text(Level.SENSOR, "Receive body sensor")

            self._body.parse(message, self._current_time)

            self._see_state.update_by_sense_body(self._current_time, self._body.view_width(), self._body.view_quality())

            self._agent._effector.check_command_count(self._body)
            self._agent.world().update_after_sense_body(self._body, self._agent._effector, self._current_time)
            # TODO CHECK HERE FOR SEPARATE WORLD

        def visual_parser(self, message: str):
            if ServerParam.i().is_fullstate(self._agent.world().our_side()) and not team_config.FULL_STATE_DEBUG:
                return
            self.parse_cycle_info(message, False)

            self._visual.parse(message,
                               self._team_name,
                               self._current_time)

            self._see_state.update_by_see(self._current_time,
                                          self._agent.world().self().view_width(),
                                          self._agent.world().self().view_quality())

            if self._visual.time() == self._current_time and \
                self._agent.world().see_time() != self._current_time:
                    self._agent.world().update_after_see(self._visual,
                                                         self._body,
                                                         self._agent.effector(),
                                                         self._current_time)

        def hear_parser(self, message: str):
            self.parse_cycle_info(message, False)
            _, cycle, sender = tuple(
                message.split(" ")[:3]
            )
            cycle = int(cycle)

            if sender[0].isnumeric() or sender[0] == '-': # PLAYER MESSAGE
                self.hear_player_parser(message)
            elif sender == "referee":
                self.hear_referee_parser(message)

        def hear_player_parser(self, message:str):
            if message.find('"') == -1:
                return
            data = message.strip('()').split(' ')
            if len(data) < 6:
                debug_print("(hear player parser) message format is not matched!")
                return
            player_message = message.split('"')[1]
            if not data[4].isdigit():
                return
            sender = int(data[4])


            Messenger.decode_all(self._agent.world()._messenger_memory,
                                 player_message,
                                 sender,
                                 self._current_time)

        def hear_referee_parser(self, message: str):
            mode = message.split(" ")[-1].strip(")")
            if not self._game_mode.update(mode, self._current_time):
                return

            # TODO CARDS AND OTHER STUFF

            self.update_server_status()

            if self._game_mode.type() is GameModeType.TimeOver:
                self.send_bye_command()
                return
            self._agent.world().update_game_mode(self._game_mode, self._current_time)
            if ServerParam.i().is_fullstate(self._agent.world().our_side()) and team_config.FULL_STATE_DEBUG:
                self._agent.full_world().update_game_mode(self._game_mode, self._current_time)


        def update_server_status(self):
            if self._server_cycle_stopped:
                self._server_cycle_stopped = False

            if self._game_mode.is_server_cycle_stopped_mode():
                self._server_cycle_stopped = True

        def parse_cycle_info(self, msg: str, by_sense_body: bool):
            cycle = int(msg.split(' ')[1].removesuffix(')\x00'))
            self.update_current_time(cycle, by_sense_body)

        def update_current_time(self, new_time: int, by_sense_body: bool):
            old_time: GameTime = self._current_time.copy()

            if self._server_cycle_stopped:
                if new_time != self._current_time.cycle():
                    self._current_time.assign(new_time, 0)

                    if new_time - 1 != old_time.cycle():
                        debug_print(f"player({self._agent.world().self_unum()}):"
                              f"last server time was wrong maybe")
                else:
                    if by_sense_body:
                        self._current_time.assign(self._current_time.cycle(), self._current_time.stopped_cycle() + 1)
                        dlog.add_text(Level.LEVEL_ANY, f"Cycle: {self._current_time.cycle()}-"
                                                       f"{self._current_time.stopped_cycle()} " + '-' * 20)

                        if self._last_decision_time != old_time and old_time.stopped_cycle() != 0:
                            dlog.add_text(Level.SYSTEM, f"(update current time) missed last action(1)")
            else:
                self._current_time.assign(new_time, 0)
                if old_time.cycle() != new_time:
                    dlog.add_text(Level.LEVEL_ANY, f"Cycle {new_time}-0 " + '-' * 20)

                    if new_time - 1 != old_time.cycle():
                        debug_print(f"player({self._agent.world().self_unum()}):"
                              f"last server time was wrong maybe")

                    if (self._last_decision_time.stopped_cycle() == 0
                            and self._last_decision_time.cycle() != new_time - 1):
                        dlog.add_text(Level.SYSTEM, f"(update current time) missed last action(2)")

        def think_received(self):
            return self._think_received

        def is_decision_time(self, msec_from_sense: int, timeout_count: int):
            SP = ServerParam.i()

            if SP.synch_mode():
                return False

            if msec_from_sense < 0:
                return False

            if self._last_decision_time == self._current_time:
                return False

            if self._agent.world().self().unum() == UNUM_UNKNOWN:
                return False

            if self._agent.world().see_time() == self._current_time:
                return True

            wait_thr:int = (team_config.WAIT_TIME_THR_SYNCH_VIEW
                            if self._see_state.is_synch()
                            else team_config.WAIT_TIME_THR_NOSYNCH_VIEW)

            if self._last_decision_time == self._agent.world().sense_body_time() and timeout_count <= 2:
                return False

            if SeeState.synch_see_mode() and SP.synch_see_offset() > wait_thr and msec_from_sense >= 0:
                return True

            if self._see_state.is_synch() and self._see_state.cycles_till_next_see() > 0:
                return True

            if msec_from_sense >= wait_thr * SP.slow_down_factor():
                return True
            return False

        def do_neck_action(self):
            debug_print(f"dna {self._neck_action}")
            if self._neck_action:
                self._neck_action.execute(self._agent)
                self._neck_action = None

        def do_view_action(self):
            if self._view_action:
                self._view_action.execute(self._agent)
                self._view_action = None

        def do_change_focus_action(self):
            if self._focus_point_action:
                self._focus_point_action.execute(self._agent)
                self._focus_point_action = None

    def __init__(self):
        super().__init__()
        self._impl: PlayerAgent.Impl = PlayerAgent.Impl(self)
        self._world = WorldModel()
        self._full_world = WorldModel()
        self._last_body_command = []
        self._is_synch_mode = True
        self._debug_client = DebugClient()
        self._effector = ActionEffector(self)

    def init_impl(self, goalie: bool) -> bool:
        self._impl._goalie = goalie

    def handle_start(self):
        if self._client is None:
            return False

        if team_config.PLAYER_VERSION < 18:
            debug_print("PYRUS2D base code does not support player version less than 18.")
            self._client.set_server_alive(False)
            return False

        # TODO check for config.host not empty

        if not self._client.connect_to(IPAddress(team_config.HOST, team_config.PLAYER_PORT)):
            debug_print("ERROR failed to connect to server")
            self._client.set_server_alive(False)
            return False

        self._impl.send_init_command()
        return True

    def handle_exit(self):
        if self._client.is_server_alive():
            self._impl.send_bye_command()
        debug_print(f"player( {self._world.self_unum()} ): finished")  # TODO : Not working

    def handle_message(self):
        self.run()

    def see_state(self):
        return self._impl._see_state

    def run(self):
        last_time_rec = time.time()
        waited_msec:int = 0
        timeout_count:int = 0
        while True:
            message_and_address = []
            message_count = 0
            while True:
                self._client.recv_message(message_and_address)
                message = message_and_address[0]
                server_address = message_and_address[1]
                if len(message) != 0:
                    self.parse_message(message.decode())

                    last_time_rec = time.time()
                    waited_msec = 0
                    timeout_count = 0
                    break

                elif time.time() - last_time_rec > 3:
                    self._client.set_server_alive(False)
                    break
                message_count += 1
                if self._impl.think_received():
                    last_time_rec = time.time()
                    break

                waited_msec+= team_config.SOCKET_INTERVAL
                timeout_count += 1
                self.handle_timeout(timeout_count, waited_msec)

            if not self._client.is_server_alive():
                debug_print(f"{team_config.TEAM_NAME} Agent : Server Down")
                break

            if self._impl.think_received():
                self.action()
                self.debug_players()
                self._impl._think_received = False
            elif not ServerParam.i().synch_mode():
                if (self._impl._last_decision_time != self._impl._current_time
                    and self.world().see_time() == self._impl._current_time):

                    self.action() # TODO CHECK

    def handle_timeout(self, timeout_count: int, waited_msec: int):
        msec_from_sense = -1
        if self._impl._body_time_stamp:
            msec_from_sense = get_time_msec() - self._impl._body_time_stamp

        if self._impl.is_decision_time(msec_from_sense, timeout_count):
            self.action()

    def debug_players(self):
        for p in self.world()._teammates + self.world()._opponents + self.world()._unknown_players:
            if p.pos_valid():
                dlog.add_circle(Level.WORLD, 1, center=p.pos(), color=Color(string='blue'))
        if self.world().ball().pos_valid():
            dlog.add_circle(Level.WORLD, center=self.world().ball().pos(), r = 0.5, color=Color(string="blue"), fill=True)

        if ServerParam.i().is_fullstate(self.world().our_side()) and team_config.FULL_STATE_DEBUG:
            for p in self.full_world()._teammates + self.full_world()._opponents + self.full_world()._unknown_players:
                if p.pos_valid():
                    dlog.add_circle(Level.WORLD, 1, center=p.pos(), color=Color(string='red'))
            if self.world().ball().pos_valid():
                dlog.add_circle(Level.WORLD, center=self.world().ball().pos(), r=0.5, color=Color(string="red"),
                                fill=True)

    def parse_message(self, message: str):
        if message.startswith("(init"):
            self.parse_init(message)
        if message.startswith("(server_param"):
            ServerParam.i().parse(message)
        if message.startswith("(sense_body"):
            self._impl.sense_body_parser(message)
            KickTable.instance().create_tables()
        if message.startswith("(see"):
            self._impl.visual_parser(message)
        if message.startswith("(hear"):
            self._impl.hear_parser(message)
        if message.startswith("(fullstate"):
            self._full_world.parse(message)
        if message.startswith("(player_type") or message.startswith("(sense_body") or message.startswith("(init"):
            self._world.parse(message)
            self._full_world.parse(message)
        if message.startswith("(think"):
            self._impl._think_received = True

    def do_dash(self, power, angle=0):
        if self.world().self().is_frozen():
            debug_print(f"(do dash) player({self._world.self_unum()} is frozen!")
            return False
        self._last_body_command.append(self._effector.set_dash(power, float(angle)))
        return True

    def do_turn(self, angle):
        if self.world().self().is_frozen():
            debug_print(f"(do turn) player({self._world.self_unum()} is frozen!")
            return False
        self._last_body_command.append(self._effector.set_turn(float(angle)))
        return True

    def do_move(self, x, y):
        if self.world().self().is_frozen():
            debug_print(f"(do move) player({self._world.self_unum()} is frozen!")
            return False
        self._last_body_command.append(self._effector.set_move(x, y))
        return True

    def do_kick(self, power: float, rel_dir: AngleDeg):
        if self.world().self().is_frozen():
            debug_print(f"(do kick) player({self._world.self_unum()} is frozen!")
            return False
        self._last_body_command.append(self._effector.set_kick(power, rel_dir))
        return True

    def do_tackle(self, power_or_dir: float, foul: bool):
        if self.world().self().is_frozen():
            debug_print(f"(do tackle) player({self._world.self_unum()} is frozen!")
            return False
        self._last_body_command.append(self._effector.set_tackle(power_or_dir, foul))
        return True

    def do_catch(self):
        wm = self.world()
        if wm.self().is_frozen():
            debug_print(f"(do catch) player({self._world.self_unum()} is frozen!")
            return False

        if not wm.self().goalie():
            debug_print(f"(do catch) player({self._world.self_unum()} is not goalie!")
            return False

        if wm.game_mode().type() is not GameModeType.PlayOn and not wm.game_mode().type().is_penalty_taken():
            debug_print(f"(do catch) player({self._world.self_unum()} play mode is not play_on!")
            return False

        if not wm.ball().rpos_valid():
            debug_print(f"(do catch) player({self._world.self_unum()} ball rpos is not valid!")
            return False

        self._last_body_command.append(self.effector().set_catch())




    def do_turn_neck(self, moment: AngleDeg) -> bool:
        self._last_body_command.append(self._effector.set_turn_neck(moment))
        return True

    def do_change_view(self, width: ViewWidth) -> bool:
        self._last_body_command.append(self._effector.set_change_view(width))
        return True

    def do_change_focus(self, moment_dist: float, moment_dir: Union[float, AngleDeg]):
        if isinstance(moment_dir, float) or isinstance(moment_dir, int):
            moment_dir = AngleDeg(moment_dir)

        aligned_moment_dist = moment_dist
        if self.world().self().focus_point_dist() + aligned_moment_dist < 0.0:
            debug_print(f"(do_change_focus) player({self._world.self_unum()} focus dist can not be less than 0")
            aligned_moment_dist = -self.world().self().focus_point_dist()
        if self.world().self().focus_point_dist() + aligned_moment_dist > 40.0:
            debug_print(f"(do_change_focus) player({self._world.self_unum()} focus dist can not be more than 40")
            aligned_moment_dist = 40.0 - self.world().self().focus_point_dist()
        next_view = self.effector().queued_next_view_width()
        next_half_angle = next_view.width() * 0.5

        aligned_moment_dir = moment_dir
        focus_point_dir_after_change_view = AngleDeg(min_max(-next_half_angle, self.world().self().focus_point_dir().degree(), next_half_angle))
        if focus_point_dir_after_change_view.degree() + aligned_moment_dir.degree() < -next_half_angle:
            aligned_moment_dir = -next_half_angle - focus_point_dir_after_change_view.degree()
        elif focus_point_dir_after_change_view.degree() + aligned_moment_dir.degree() > next_half_angle:
            aligned_moment_dir = next_half_angle - focus_point_dir_after_change_view.degree()

        self._last_body_command.append(self._effector.set_change_focus(aligned_moment_dist, aligned_moment_dir))

        return True

    def add_say_message(self, message: Messenger):
        self._effector.add_say_message(message)

    def do_attentionto(self, side: SideID, unum: int):
        if side is SideID.NEUTRAL:
            debug_print("(player agent do attentionto) side is neutral!")
            return

        if unum == UNUM_UNKNOWN or not (1<= unum <= 11):
            debug_print(f"(player agent do attentionto) unum is not in range! unum={unum}")
            return

        if self.world().our_side() == side and self.world().self().unum() == unum:
            debug_print(f"(player agent do attentionto) attentioning to self!")
            return

        if self.world().self().attentionto_side() == side and self.world().self().attentionto_unum() == unum:
            debug_print(f"(player agent do attentionto) already attended to the player! unum={unum}")
            return

        self._last_body_command.append(self._effector.set_attentionto(side, unum))

    def do_attentionto_off(self):
        self._last_body_command.append(self._effector.set_attentionto_off())

    if team_config.FULL_STATE_DEBUG:
        def world(self):
            return self._world
    else:
        def world(self) -> WorldModel:
            return self._full_world

    def full_world(self) -> WorldModel:
        return self._full_world

    def debug_client(self) -> DebugClient:
        return self._debug_client

    def effector(self):
        return self._effector

    def action_impl(self):
        pass

    def action(self):
        if (self.world().self_unum() is None
                or self.world().self().unum() != self.world().self_unum()):
            return

        self.world().update_just_before_decision(self._effector, self._impl._current_time)
        if ServerParam.i().is_fullstate(self._world.our_side()) and team_config.FULL_STATE_DEBUG:
            self.full_world().update_just_before_decision(self._effector, self._impl._current_time)

        self._effector.reset()

        self.action_impl()
        self._impl.do_view_action()
        self._impl.do_neck_action()
        self._impl.do_change_focus_action()
        self._impl._last_decision_time = self._impl._current_time.copy()

        self.world().update_just_after_decision(self._effector)
        self._impl._see_state.set_view_mode(self.world().self().view_width(),
                                            self.world().self().view_quality())

        message_command = self._effector.make_say_message_command(self.world())
        if message_command:
            self._last_body_command.append(message_command)
        commands = self._last_body_command
        # if self.world().our_side() == SideID.RIGHT:
        # PlayerCommandReverser.reverse(commands) # unused :\ # its useful :) # nope not useful at all :(
        if self._is_synch_mode:
            commands.append(PlayerDoneCommand())
        message = self.make_commands(commands)

        self._client.send_message(message)
        self._debug_client.write_all(self.world(), None)  # TODO add action effector
        dlog.flush()
        self._last_body_command = []
        self._effector.clear_all_commands()

    def make_commands(self, commands):
        self._effector.update_after_actions()

        message = PlayerSendCommands.all_to_str(commands)
        return message

    def parse_init(self, message):
        message = message.split(" ")
        unum = int(message[2])
        side = message[1]

        self._world.init(self._impl._team_name, side, unum, self._impl._goalie)
        if ServerParam.i().is_fullstate(side) and team_config.FULL_STATE_DEBUG:
            self._full_world.init(self._impl._team_name, side, unum, False)
        dlog.setup_logger(f"dlog{side}{unum}", f"/tmp/{self._impl._team_name}-{unum}.log", logging.DEBUG)

    def set_view_action(self, view_action: ViewAction):
        self._impl._view_action = view_action

    def set_neck_action(self, neck_action: NeckAction):
        self._impl._neck_action = neck_action

    def set_focus_point_action(self, focus_point_action: FocusPointAction):
        self._impl._focus_point_action = focus_point_action