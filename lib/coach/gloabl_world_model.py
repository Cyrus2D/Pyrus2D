from lib.coach.global_object import GlobalPlayerObject, GlobalBallObject
from lib.debug.debug import log
from lib.parser.global_message_parser import GlobalFullStateWorldMessageParser
from lib.player.object_player import *
from lib.player.object_ball import *
from lib.rcsc.game_mode import GameMode
from lib.rcsc.game_time import GameTime
from lib.rcsc.types import HETERO_DEFAULT, HETERO_UNKNOWN, GameModeType


class GlobalWorldModel:
    def __init__(self):
        self._player_types = [PlayerType() for _ in range(18)]
        self._team_name_l: str = ""
        self._team_name_r: str = ""
        self._our_side: SideID = SideID.NEUTRAL
        self._our_players: list[GlobalPlayerObject] = [GlobalPlayerObject() for _ in range(11)]
        self._their_players: list[GlobalPlayerObject] = [GlobalPlayerObject() for _ in range(11)]
        self._unknown_player: list[GlobalPlayerObject] = [GlobalPlayerObject() for _ in range(22)]
        self._ball: GlobalBallObject = GlobalBallObject()
        self._time: GameTime = GameTime(-1, 0)
        self._game_mode: GameMode = GameMode()
        self._last_kicker_side: SideID = SideID.NEUTRAL
        self._yellow_card_left: list[bool] = [False for _ in range(11)]
        self._yellow_card_right: list[bool] = [False for _ in range(11)]
        self._red_card_left: list[bool] = [False for _ in range(11)]
        self._red_card_right: list[bool] = [False for _ in range(11)]
        
        self._last_playon_start: int = 0
        self._freeform_allowed_count: int = ServerParam.i().coach_say_count_max()  
        self._freeform_send_count: int = 0
        
        self._subsititute_count: dict[SideID, int] = {
            SideID.LEFT: 0,
            SideID.RIGHT: 0
        }
        
        self._our_player_type_id: list[int] = [HETERO_DEFAULT for _ in range(11)]
        self._their_player_type_id: list[int] = [HETERO_DEFAULT for _ in range(11)]
        
        self._our_player_type_used_count: list[int] = [11]
        self._their_player_type_used_count: list[int] = [11]
        
        self._available_player_type_id: list[int] = [HETERO_DEFAULT]
        
    
    def player_types(self):
        return self._player_types

    def ball(self) -> GlobalBallObject:
        return self._ball

    def our_side(self):
        return SideID.RIGHT if self._our_side == 'r' else SideID.LEFT if self._our_side == 'l' else SideID.NEUTRAL
    
    def their_side(self):
        return self.our_side().invert()        

    def our_player(self, unum):
        return self._our_players[unum - 1]

    def their_player(self, unum):
        return self._their_players[unum - 1]

    def time(self):
        return self._time.copy()
    
    def available_player_type_id(self):
        return self._available_player_type_id

    def parse(self, message):
        if message.find("see_global") != -1:
            self.fullstate_parser(message)
        elif 0 < message.find("player_type") < 3:
            self.player_type_parser(message)
        elif message.find("sense_body") != -1:
            pass
        elif message.find("init") != -1:
            pass

    def fullstate_parser(self, message):
        parser = GlobalFullStateWorldMessageParser()
        parser.parse(message)
        self._team_name_l = parser.dic()['teams']['team_left']
        self._team_name_r = parser.dic()['teams']['team_right']

        # TODO vmode counters and arm

        self._ball.init_str(parser.dic()['b'])

        if 'players' in parser.dic():
            for player_dic in parser.dic()['players']:
                player = GlobalPlayerObject()
                player.init_dic(player_dic)
                # player.set_player_type(self._player_types[player.type()])
                if player.side().value == self._our_side:
                    self._our_players[player.unum() - 1] = player
                elif player.side() == SideID.NEUTRAL:
                    self._unknown_player[player.unum() - 1] = player
                else:
                    self._their_players[player.unum() - 1] = player
            # TODO check reversion

    def __repr__(self):
        # Fixed By MM _ temp
        return "(time: {})(ball: {})(tm: {})(opp: {})".format(self._time, self.ball(), self._our_players,
                                                              self._their_players)

    def self_parser(self, message):
        message = message.split(" ")
        self._self_unum = int(message[2])
        self._our_side = message[1]
    
    def update_after_see(self, current_time: GameTime):
        self._time = current_time.copy()

    def player_type_parser(self, message):
        new_player_type = PlayerType()
        new_player_type.parse(message)
        self._player_types[new_player_type.id()] = new_player_type
        self._available_player_type_id.append(new_player_type.id())

    def reverse(self):
        self.ball().reverse()
        Object.reverse_list(self._our_players)
        Object.reverse_list(self._their_players)

    def team_name_l(self):
        return self._team_name_l

    def team_name_r(self):
        return self._team_name_r

    def game_mode(self):
        return self._game_mode

    def last_kicker_side(self) -> SideID:
        return self._last_kicker_side

    def can_send_free_form(self):
        if 0 <= self._freeform_allowed_count <= self._freeform_send_count:
            return False
        
        if self.game_mode().type() is not GameModeType.PlayOn:
            return True
        
        playon_period = self.time().cycle() - self._last_playon_start
        wait_period = ServerParam.i().freeform_wait_period()
        if playon_period > wait_period:
            playon_period %= wait_period
            return playon_period < ServerParam.i().freeform_send_period()
        return False
    
    def inc_free_form_send_count(self):
        self._freeform_send_count += 1
    
    def update_game_mode(self, game_mode: GameMode, current_time: GameTime):
        pk_mode = game_mode.is_penalty_kick_mode()
        if not pk_mode and self._game_mode.type() is not  GameModeType.PlayOn:
            if game_mode.type() != self.game_mode().type():
                self._last_set_play_start_time = current_time.copy()
                self._set_play_count = 0
            
            if game_mode.type().is_goal_kick():
                self._ball.update_only_vel(Vector2D(0, 0), 0)
        
        if self._game_mode.type() is not GameModeType.PlayOn and game_mode.type() is GameModeType.PlayOn:
            self._last_playon_start = current_time.cycle()        
        
        self._game_mode = game_mode.copy()
        self._time = current_time.copy()
    
    def our_subsititute_count(self):
        return self._subsititute_count[self.our_side()]
    
    def their_subsititute_count(self):
        return self._subsititute_count[self.our_side().invert()]
    
    def change_player_type(self, side: SideID, unum: int, type: int):
        if side is SideID.NEUTRAL or not(1<=unum<=11):
            log.os_log().error(f"(change player type) unum or side is not standard. side={side} unum={unum}")
            return
        
        player_types = len(self.player_types())
        if type != HETERO_UNKNOWN and not (HETERO_DEFAULT <= type < type):
            log.os_log().error(f"(change player type) undefined type. type={type}")
            return
        
        if side == self.our_side() or (self.our_side() is SideID.NEUTRAL and side is SideID.LEFT):
            self._our_player_type_id[unum - 1] = type
            
            if self._time.cycle() > 0:
                self._subsititute_count[self.our_side()] += 1

            self._our_player_type_used_count = [0 for _ in range(player_types)]
            for i in range(11):
                pt = self._our_player_type_id[i]
                if pt != HETERO_UNKNOWN:
                    self._our_player_type_used_count[pt] += 1
                 # TODO CARD
        else:
            self._their_player_type_id[unum - 1] = type
            
            if self._time.cycle() > 0:
                self._subsititute_count[self.our_side().invert()] += 1
            
            self._their_player_type_used_count = [0 for _ in range(player_types)]
            for i in range(11):
                pt = self._their_player_type_id[i]
                if pt != HETERO_UNKNOWN:
                    self._their_player_type_used_count[pt] += 1
                 # TODO CARD
        
        if side == self.our_side():
            for pt in self._available_player_type_id:
                if pt == type:
                    self._available_player_type_id.remove(pt)
                    break
        
    def update_player_type(self):
        if self.our_side() is SideID.NEUTRAL:
            return
        
        self._our_player_type_used_count = [0 for _ in range(18)]
        for i in range(11):
            pt = self._our_player_type_id[i]
            if pt != HETERO_UNKNOWN:
                self._our_player_type_used_count[pt] += 1
        
        self._their_player_type_used_count = [0 for _ in range(18)]
        for i in range(11):
            pt = self._their_player_type_id[i]
            if pt != HETERO_UNKNOWN:
                self._their_player_type_used_count[pt] += 1

    def team_name_left(self):
        return self._team_name_l

    def team_name_right(self):
        return self._team_name_r
            
            
            
        