import logging
import time

from lib.action.kick_table import KickTable
from base.decision import get_decision
from lib.debug.level import Level
from lib.debug.logger import dlog
from lib.math.angle_deg import AngleDeg
from lib.player.sensor.body_sensor import BodySensor
from lib.player.sensor.see_state import SeeState
from lib.player.soccer_agent import SoccerAgent
from lib.player.world_model import WorldModel
from lib.network.udp_socket import IPAddress
from lib.player_command.player_command import PlayerInitCommand, PlayerByeCommand
from lib.player_command.player_command_body import PlayerTurnCommand, PlayerDashCommand, PlayerMoveCommand, \
    PlayerKickCommand, PlayerTackleCommand
from lib.player_command.player_command_support import PlayerDoneCommand, PlayerTurnNeckCommand
from lib.player_command.player_command_sender import PlayerSendCommands
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.player.debug_client import DebugClient


class PlayerAgent(SoccerAgent):
    class Impl:
        def __init__(self, agent):
            # TODO so many things....
            self._agent: PlayerAgent = agent
            self._think_received = False
            self._current_time: GameTime = GameTime()
            self._server_cycle_stopped: bool = False
            self._last_decision_time: GameTime = GameTime()
            self._body = BodySensor()
            self._see_state: SeeState = SeeState()

        def send_init_command(self):
            # TODO check reconnection

            # TODO make config class for these data
            com = PlayerInitCommand("Pyrus", 15, False)
            # TODO set team name from config
            self._agent._full_world._team_name = "Pyrus"

            if self._agent._client.send_message(com.str()) <= 0:
                print("ERROR failed to connect to server")
                self._agent._client.set_server_alive(False)

        def send_bye_command(self):
            com = PlayerByeCommand()
            self._agent._client.send_message(com.str())
            self._agent._client.set_server_alive(False)

        def sense_body_parser(self, message: str):
            self.parse_cycle_info(message, True)

            dlog.add_text(Level.SENSOR, "Receive body sensor")

            self._body.parse(message, self._current_time)

            self.see_state_.update_by_sense_body(self._time, self._body.view_width(), self._body.view_quality())

            # todo action counters
            self.update_after_sense_body(self._body, )

        def parse_cycle_info(self, msg: str, by_sense_body: bool):
            cycle = int(msg.split(' ')[1].strip(')('))
            self.update_current_time(cycle, by_sense_body)

        def update_current_time(self, new_time: int, by_sense_body: bool):
            old_time: GameTime = self._current_time.copy()

            if self._server_cycle_stopped:
                if new_time != self._current_time.cycle():
                    self._current_time.assign(new_time, 0)

                    if new_time - 1 != old_time.cycle():
                        print(f"player_n({self._agent.world().self_unum()}):"
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
                        print(f"player_n({self._agent.world().self_unum()}):"
                              f"last server time was wrong maybe")

                    if (self._last_decision_time.stopped_cycle() == 0
                            and self._last_decision_time.cycle() != new_time - 1):
                        dlog.add_text(Level.SYSTEM, f"(update current time) missed last action(2)")

        @property
        def think_received(self):
            return self._think_received

    def __init__(self):
        super().__init__()
        self._impl: PlayerAgent.Impl = PlayerAgent.Impl(self)
        self._world = WorldModel()
        self._full_world = WorldModel()
        self._last_body_command = []
        self._is_synch_mode = True
        self._debug_client = DebugClient()

    def handle_start(self):
        if self._client is None:
            return False

        # TODO check for config.host not empty

        if not self._client.connect_to(IPAddress('localhost', 6000)):
            print("ERROR failed to connect to server")
            self._client.set_server_alive(False)
            return False

        self._impl.send_init_command()
        return True

    def handle_exit(self):
        if self._client.is_server_alive():
            self._impl.send_bye_command()
        print(f"player( {self._world.self_unum()} ): finished")  # TODO : Not working

    def handle_message(self):
        self.run()

    def see_state(self):
        return self._impl._see_state

    def run(self):
        last_time_rec = time.time()
        while True:
            message_and_address = []
            message_count = 0
            while True:
                self._client.recv_message(message_and_address)
                message = message_and_address[0]
                server_address = message_and_address[1]
                if len(message) != 0:
                    self.parse_message(message.decode())
                elif time.time() - last_time_rec > 3:
                    self._client.set_server_alive(False)
                    break
                message_count += 1
                if self._impl.think_received:
                    last_time_rec = time.time()
                    break

            if not self._client.is_server_alive():
                print("Pyrus Agent : Server Down")
                # print("Pyrus Agent", self._world.self_unum(), ": Server Down")
                break

            if self._impl.think_received:
                self.action()
                self._impl._think_received = False
            # TODO elif for not sync mode

    def parse_message(self, message):
        if message.find("(init") != -1:
            self.init_dlog(message)
        if message.find("server_param") != -1:
            ServerParam.i().parse(message)
        if message.find("sense_body") != -1:
            self._impl.sense_body_parser(message)

            # TODO make function for these things
            if KickTable.instance().create_tables():
                print("KICKTABLE CREATE")
            else:
                print("KICKTABLE Faild")
        elif message.find("fullstate") != -1 or message.find("player_type") != -1 or message.find(
                "sense_body") != -1 or message.find("(init") != -1:
            self._full_world.parse(message)
            dlog._time = self.world().time()
        elif message.find("think") != -1:
            self._impl._think_received = True

    def do_dash(self, power, angle=0):
        self._last_body_command.append(PlayerDashCommand(power, float(angle)))
        return True

    def do_turn(self, angle):
        self._last_body_command.append(PlayerTurnCommand(float(angle)))
        return True

    def do_move(self, x, y):
        self._last_body_command.append(PlayerMoveCommand(x, y))
        return True

    def do_kick(self, power: float, rel_dir: AngleDeg):
        self._last_body_command.append(PlayerKickCommand(power, rel_dir))
        return True

    def do_tackle(self, power_or_dir: float, foul: bool):  # TODO : tons of work
        if self.world().self().is_frozen():
            return False
        self._last_body_command.append(PlayerTackleCommand(power_or_dir, foul))
        return True

    def do_turn_neck(self, moment: AngleDeg) -> bool:
        self._last_body_command.append(PlayerTurnNeckCommand(moment))
        return True

    def world(self) -> WorldModel:
        return self._full_world

    def full_world(self) -> WorldModel:
        return self._full_world

    def debug_client(self) -> DebugClient:
        return self._debug_client

    def action(self):
        if (self.world().self_unum() is None
                or self.world().self().unum() != self.world().self_unum()):
            return
        get_decision(self)
        commands = self._last_body_command
        # if self.world().our_side() == SideID.RIGHT:
        # PlayerCommandReverser.reverse(commands) # unused :\ # its useful :) # nope not useful at all :(
        if self._is_synch_mode:
            commands.append(PlayerDoneCommand())
        self._client.send_message(PlayerSendCommands.all_to_str(commands))
        self._debug_client.write_all(self.world(), None)  # TODO add action effector
        dlog.flush()
        self._last_body_command = []

    def init_dlog(self, message):
        message = message.split(" ")
        unum = int(message[2])
        side = message[1]
        dlog.setup_logger(f"dlog{side}{unum}", f"/tmp/{self.world().team_name()}-{unum}.log", logging.DEBUG)
