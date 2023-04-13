from math import exp

from pyrusgeom.soccer_math import bound

import team_config
from base.strategy import Strategy
from lib.debug.debug import log
from lib.messenger.ball_goalie_messenger import BallGoalieMessenger
from lib.messenger.ball_messenger import BallMessenger
from lib.messenger.ball_player_messenger import BallPlayerMessenger
from lib.messenger.ball_pos_vel_messenger import BallPosVelMessenger
from lib.messenger.goalie_messenger import GoalieMessenger
from lib.messenger.goalie_player_messenger import GoaliePlayerMessenger
from lib.messenger.messenger import Messenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.messenger.one_player_messenger import OnePlayerMessenger
from lib.messenger.recovery_message import RecoveryMessenger
from lib.messenger.stamina_messenger import StaminaMessenger
from lib.messenger.three_player_messenger import ThreePlayerMessenger
from lib.messenger.two_player_messenger import TwoPlayerMessenger
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import UNUM_UNKNOWN, GameModeType, SideID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent
    from lib.player.object_player import PlayerObject
    from lib.player.world_model import WorldModel


class ObjectScore:
    def __init__(self, n=UNUM_UNKNOWN, score=-1000, player=None):
        self.number = n
        self.score = score
        self.player: PlayerObject = player


class SampleCommunication:
    def __init__(self):
        self._current_sender_unum: int = UNUM_UNKNOWN
        self._next_sender_unum: int = UNUM_UNKNOWN
        self._ball_send_time: GameTime = GameTime(0, 0)
        self._teammate_send_time: list[GameTime] = [GameTime(0, 0) for i in range(12)]
        self._opponent_send_time: list[GameTime] = [GameTime(0, 0) for i in range(12)]

    def should_say_ball(self, agent: 'PlayerAgent'):
        wm = agent.world()
        ef = agent.effector()

        if wm.ball().seen_pos_count() > 0 or wm.ball().seen_vel_count() > 2:
            return False
        if wm.game_mode().type() != GameModeType.PlayOn and ef.queued_next_ball_vel().r2() < 0.5 ** 2:
            return False
        if wm.kickable_teammate():
            return False

        ball_vel_changed = False
        current_ball_speed = wm.ball().vel().r()

        if wm.prev_ball().vel_valid():
            prev_ball_speed = wm.prev_ball().vel().r()
            angle_diff = (wm.ball().vel().th() - wm.prev_ball().vel().th()).abs()

            log.sw_log().communication().add_text(f'(sample communication)'
                                       f'prev vel={wm.prev_ball().vel()}, r={prev_ball_speed}'
                                       f'current_vel={wm.ball().vel()}, r={wm.ball().vel()}')

            if current_ball_speed > prev_ball_speed + 0.1 \
                    or (
                    prev_ball_speed > 0.5 and current_ball_speed < prev_ball_speed * ServerParam.i().ball_decay() / 2) \
                    or (prev_ball_speed > 0.5 and angle_diff > 20.):
                log.sw_log().communication().add_text(f'(sample communication) ball vel changed')
                ball_vel_changed = True

        if wm.self().is_kickable():
            if ball_vel_changed and wm.last_kicker_side() != wm.our_side() and not wm.kickable_opponent():
                log.sw_log().communication().add_text(
                    "(sample communication) ball vel changed. opponent kicked. no opponent kicker")
                return True
            if ef.queued_next_ball_kickable() and current_ball_speed < 1.:
                return False
            if ball_vel_changed and ef.queued_next_ball_vel().r() > 1.:
                log.sw_log().communication().add_text('(sample communication) kickable. ball vel changed')
                return True
            log.sw_log().communication().add_text('(sample communication) kickable. but no say')
            return False

        ball_nearest_teammate: PlayerObject = None
        second_ball_nearest_teammate: PlayerObject = None

        for p in wm.teammates_from_ball():
            if p is None:
                continue
            if p.is_ghost() or p.pos_count() >= 10:
                continue

            if ball_nearest_teammate is None:
                ball_nearest_teammate = p
            elif second_ball_nearest_teammate is None:
                second_ball_nearest_teammate = p
                break

        our_min = min(wm.intercept_table().self_reach_cycle(), wm.intercept_table().teammate_reach_cycle())
        opp_min = wm.intercept_table().opponent_reach_cycle()

        if ball_nearest_teammate is None \
                or ball_nearest_teammate.dist_from_ball() > wm.ball().dist_from_self() - 3.:
            log.sw_log().communication().add_text('(sample communication) maybe nearest to ball')

            if ball_vel_changed or (opp_min <= 1 and current_ball_speed > 1.):
                log.sw_log().communication().add_text('(sample communication) nearest to ball. ball vel changed?')
                return True

        if ball_nearest_teammate is not None \
                and wm.ball().dist_from_self() < 20. \
                and 1. < ball_nearest_teammate.dist_from_ball() < 6. \
                and (opp_min <= our_min + 1 or ball_vel_changed):
            log.sw_log().communication().add_text('(sample communication) support nearset player')
            return True
        return False

    def should_say_opponent_goalie(self, agent: 'PlayerAgent'):
        wm = agent.world()
        goalie: PlayerObject = wm.get_their_goalie()

        if goalie is None:
            return False

        if goalie.seen_pos_count() == 0 \
                and goalie.body_count() == 0 \
                and goalie.unum() != UNUM_UNKNOWN \
                and goalie.unum_count() == 0 \
                and goalie.dist_from_self() < 25. \
                and 51. - 16. < goalie.pos().x() < 52.5 \
                and goalie.pos().abs_y() < 20.:

            goal_pos = ServerParam.i().their_team_goal_pos()
            ball_next = wm.ball().pos() + wm.ball().vel()

            if ball_next.dist2(goal_pos) < 18 ** 2:
                return True
        return False

    def update_player_send_time(self, wm: 'WorldModel', side: SideID, unum: int):
        if not (1 <= unum <= 11):
            log.os_log().error(f'(sample communication) illegal player number. unum={unum}')
            return

        if side == wm.our_side():
            self._teammate_send_time[unum] = wm.time().copy()
        else:
            self._opponent_send_time[unum] = wm.time().copy()


    def say_ball_and_players(self, agent: 'PlayerAgent'):
        SP = ServerParam.i()
        wm = agent.world()
        ef = agent.effector()

        current_len = ef.get_say_message_length()

        should_say_ball = self.should_say_ball(agent)
        should_say_goalie = self.should_say_opponent_goalie(agent)
        goalie_say_situation = False  # self.goalie_say_situation # TODO IMP FUNC

        if not should_say_ball and not should_say_goalie and not goalie_say_situation \
                and self._current_sender_unum != wm.self().unum() \
                and current_len == 0:
            log.sw_log().communication().add_text('(sample communication) say ball and players: no send situation')
            return False

        available_len = SP.player_say_msg_size() - current_len
        mm = wm.messenger_memory()

        objects = [ObjectScore(i, 1000) for i in range(23)]
        objects[0].score = wm.time().cycle() - mm.ball_time().cycle()

        for p in mm.player_record():
            n = round(p[1].unum_)
            if not (1 <= n <= 22):
                continue

            objects[n].score = wm.time().cycle() - p[0].cycle()

        if 1 <= wm.their_goalie_unum() <= 11:
            n = wm.their_goalie_unum() + 11
            diff = wm.time().cycle() - mm.goalie_time().cycle()
            objects[n].score = min(objects[n].score, diff)

        if wm.self().is_kickable():
            if ef.queued_next_ball_kickable():
                objects[0].score = -1000
            else:
                objects[0].score = 1000
        elif wm.ball().seen_pos_count() > 0 or wm.ball().seen_vel_count() > 1 or wm.kickable_teammate():
            objects[0].score = -1000
        elif should_say_ball:
            objects[0].score = 1000
        elif objects[0].score > 0:
            if wm.prev_ball().vel_valid():
                angle_diff = (wm.ball().vel().th() - wm.prev_ball().vel().th()).abs()
                prev_speed = wm.prev_ball().vel().r()
                current_speed = wm.ball().vel().r()

                if (current_speed > prev_speed + 0.1
                        or (prev_speed > 0.5 and current_speed < prev_speed * SP.ball_decay() * 0.5)
                        or (prev_speed > 0.5 and angle_diff > 20.)):
                    objects[0].score = 1000
                else:
                    objects[0].score /= 2

        variance = 30
        x_rate = 1
        y_rate = 0.5

        min_step = min(wm.intercept_table().opponent_reach_cycle(), wm.intercept_table().self_reach_cycle(),
                       wm.intercept_table().teammate_reach_cycle())
        ball_pos = wm.ball().inertia_point(min_step)

        for i in range(1, 12):
            p = wm.our_player(i)
            if p is None or p.unum_count() >= 2:
                objects[i].score = -1000
            else:
                d = (((p.pos().x() - ball_pos.x()) * x_rate) ** 2 + ((p.pos().y() - ball_pos.y()) * y_rate) ** 2) ** 0.5
                objects[i].score *= exp(-d ** 2 / (2 * variance ** 2))
                objects[i].score *= 0.3 ** p.unum_count()
                objects[i].player = p

            p = wm.their_player(i)
            if p is None or p.unum_count() >= 2:
                objects[i + 11].score = -1000
            else:
                d = (((p.pos().x() - ball_pos.x()) * x_rate) ** 2 + ((p.pos().y() - ball_pos.y()) * y_rate) ** 2) ** 0.5
                objects[i + 11].score *= exp(-d ** 2 / (2 * variance ** 2))
                objects[i + 11].score *= 0.3 ** p.unum_count()
                objects[i + 11].player = p

        objects = list(filter(lambda x: x.score > 0.1, objects))
        objects.sort(key=lambda x: x.score, reverse=True)

        can_send_ball = False
        send_ball_and_player = False
        send_players: list[ObjectScore] = []

        for o in objects:
            if o.number == 0:
                can_send_ball = True
                if len(send_players) == 1:
                    send_ball_and_player = True
                    break
            else:
                send_players.append(o)
                if can_send_ball:
                    send_ball_and_player = True
                    break

                if len(send_players) >= 3:
                    break

        if should_say_ball:
            can_send_ball = True

        ball_vel = ef.queued_next_ball_vel()
        if wm.self().is_kickable() and ef.queued_next_ball_kickable():
            ball_vel.assign(0, 0)
            log.sw_log().communication().add_text('(sample communication) next cycle is kickable')

        if wm.kickable_opponent() or wm.kickable_teammate():
            ball_vel.assign(0, 0)

        if can_send_ball and not send_ball_and_player and available_len >= Messenger.SIZES[
            Messenger.Types.BALL]:
            if available_len >= Messenger.SIZES[Messenger.Types.BALL_PLAYER]:
                agent.add_say_message(BallPlayerMessenger(ef.queued_next_ball_pos(),
                                                        ball_vel,
                                                        wm.self().unum(),
                                                        ef.queued_next_self_pos(),
                                                        ef.queued_next_self_body()))
                self.update_player_send_time(wm, wm.our_side(), wm.self().unum())
            else:
                agent.add_say_message(BallMessenger(ef.queued_next_ball_pos(), ball_vel))

            self._ball_send_time = wm.time().copy()
            log.sw_log().communication().add_text('(sample communication) only ball')
            return True

        if send_ball_and_player:
            if should_say_goalie and available_len >= Messenger.SIZES[Messenger.Types.BALL_GOALIE]:
                goalie = wm.get_their_goalie()
                agent.add_say_message(BallGoalieMessenger(ef.queued_next_ball_pos(),
                                                                 ball_vel,
                                                                 goalie.pos() + goalie.vel(),
                                                                 goalie.body()))
                self._ball_send_time = wm.time().copy()
                self.update_player_send_time(wm, goalie.side(), goalie.unum())

                log.sw_log().communication().add_text('(sample communication) ball and goalie')
                return True

            if available_len >= Messenger.SIZES[Messenger.Types.BALL_PLAYER]:
                p = send_players[0].player
                if p.unum() == wm.self().unum():
                    agent.add_say_message(BallPlayerMessenger(ef.queued_next_ball_pos(),
                                                                     ball_vel,
                                                                     wm.self().unum(),
                                                                     ef.queued_next_self_pos(),
                                                                     ef.queued_next_self_body()))
                else:
                    agent.add_say_message(BallPlayerMessenger(ef.queued_next_ball_pos(),
                                                                     ball_vel,
                                                                     send_players[0].number,
                                                                     p.pos() + p.vel(),
                                                                     p.body()))

                self._ball_send_time = wm.time().copy()
                self.update_player_send_time(wm, p.side(), p.unum())

                log.sw_log().communication().add_text(f'(sample communication) ball and player {p.side()}{p.unum()}')
                return True

        if wm.ball().pos().x() > 34 and wm.ball().pos().abs_y() < 20:
            goalie: PlayerObject = wm.get_their_goalie()

            if goalie is not None \
                    and goalie.seen_pos_count() == 0 \
                    and goalie.body_count() == 0 \
                    and goalie.pos().x() > 53. - 16 \
                    and goalie.pos().abs_y() < 20. \
                    and goalie.unum() != UNUM_UNKNOWN \
                    and goalie.dist_from_self() < 25:
                if available_len >= Messenger.SIZES[Messenger.Types.GOALIE_PLAYER]:
                    player: PlayerObject = None
                    for p in send_players:
                        if p.player.unum() != goalie.unum() and p.player.side() != goalie.side():
                            player = p.player
                            break

                    if player is not None:
                        goalie_pos = goalie.pos() + goalie.vel()
                        goalie_pos.assign(
                            bound(53. - 16., goalie_pos.x(), 52.9),
                            bound(-20, goalie_pos.y(), 20),
                        )
                        agent.add_say_message(GoaliePlayerMessenger(goalie.unum(),
                                                                           goalie_pos,
                                                                           goalie.body(),
                                                                           (
                                                                               player.unum() if player.side() == wm.our_side() else player.unum() + 11),
                                                                           player.pos() + player.vel()))
                        self.update_player_send_time(wm, goalie.side(), goalie.unum())
                        self.update_player_send_time(wm, player.side(), player.unum())

                        log.sw_log().communication().add_text(f'(sample communication) say goalie and player: '
                                                              f'goalie({goalie.unum()}): p={goalie.pos()} b={goalie.body()}'
                                                              f'player({player.side()}{player.unum()}: {player.pos()})')
                        return True

                if available_len >= Messenger.SIZES[Messenger.Types.GOALIE]:
                    goalie_pos = goalie.pos() + goalie.vel()
                    goalie_pos.assign(
                        bound(53. - 16., goalie_pos.x(), 52.9),
                        bound(-20, goalie_pos.y(), 20),
                    )
                    agent.add_say_message(GoalieMessenger(goalie.unum(),
                                                                 goalie_pos,
                                                                 goalie.body()))
                    self._ball_send_time = wm.time().copy()
                    self._opponent_send_time[goalie.unum()] = wm.time().copy()

                    log.sw_log().communication().add_text(f'(sample communication) say goalie info:'
                                                          f'{goalie.unum()} {goalie.pos()} {goalie.body()}')
                    return True

        if len(send_players) >= 3 and available_len >= Messenger.SIZES[Messenger.Types.THREE_PLAYER]:
            for o in send_players:
                log.os_log().debug(o.player)
                log.os_log().debug(o.player.pos())
            p0 = send_players[0].player
            p1 = send_players[1].player
            p2 = send_players[2].player

            agent.add_say_message(ThreePlayerMessenger(send_players[0].number,
                                                              p0.pos() + p0.vel(),
                                                              send_players[1].number,
                                                              p1.pos() + p1.vel(),
                                                              send_players[2].number,
                                                              p2.pos() + p2.vel()))
            self.update_player_send_time(wm, p0.side(), p0.unum())
            self.update_player_send_time(wm, p1.side(), p1.unum())
            self.update_player_send_time(wm, p2.side(), p2.unum())

            log.sw_log().communication().add_text(f'(sample communication) three players:'
                                                  f'{p0.side()}{p0.unum()}'
                                                  f'{p1.side()}{p1.unum()}'
                                                  f'{p2.side()}{p2.unum()}')
            return True

        if len(send_players) >= 2 and available_len >= Messenger.SIZES[Messenger.Types.TWO_PLAYER]:
            p0 = send_players[0].player
            p1 = send_players[1].player

            agent.add_say_message(TwoPlayerMessenger(send_players[0].number,
                                                            p0.pos() + p0.vel(),
                                                            send_players[1].number,
                                                            p1.pos() + p1.vel()))
            self.update_player_send_time(wm, p0.side(), p0.unum())
            self.update_player_send_time(wm, p1.side(), p1.unum())

            log.sw_log().communication().add_text(f'(sample communication) two players:'
                                                  f'{p0.side()}{p0.unum()}'
                                                  f'{p1.side()}{p1.unum()}')
            return True

        if len(send_players) >= 1 and available_len >= Messenger.SIZES[Messenger.Types.GOALIE]:
            p0 = send_players[0].player
            if p0.side() == wm.their_side() \
                    and p0.goalie() \
                    and p0.pos().x() > 53. - 16. \
                    and p0.pos().abs_y() < 20 \
                    and p0.dist_from_self() < 25:
                goalie_pos = p0.pos() + p0.vel()
                goalie_pos.assign(
                    bound(53. - 16., goalie_pos.x(), 52.9),
                    bound(-20, goalie_pos.y(), 20),
                )
                agent.add_say_message(GoalieMessenger(p0.unum(),
                                                             goalie_pos,
                                                             p0.body()))

                self.update_player_send_time(wm, p0.side(), p0.unum())

                log.sw_log().communication().add_text(f'(sample communication) goalie:'
                                                      f'{p0.side()}{p0.unum()}')
                return True

        if len(send_players) >= 1 and available_len >= Messenger.SIZES[Messenger.Types.ONE_PLAYER]:
            p0 = send_players[0].player

            agent.add_say_message(OnePlayerMessenger(send_players[0].number,
                                                            p0.pos() + p0.vel()))

            self.update_player_send_time(wm, p0.side(), p0.unum())

            log.sw_log().communication().add_text(f'(sample communication) one player:'
                                                  f'{p0.side()}{p0.unum()}')
            return True

        return False

    def update_current_sender(self, agent: 'PlayerAgent'):
        wm = agent.world()
        if agent.effector().get_say_message_length() > 0:
            self._current_sender_unum = wm.self().unum()
            return

        self._current_sender_unum = UNUM_UNKNOWN
        candidate_unum: list[int] = []

        if wm.ball().pos().x() < -10. or wm.game_mode().type() != GameModeType.PlayOn:
            for unum in range(1, 12):
                candidate_unum.append(unum)
        else:
            goalie_unum = wm.our_goalie_unum() if wm.our_goalie_unum() != UNUM_UNKNOWN else 1 # TODO STRATEGY.GOALIE_UNUM()
            for unum in range(1, 12):
                if unum != goalie_unum:
                    candidate_unum.append(unum)
        val = wm.time().cycle() + wm.time().stopped_cycle() if wm.time().stopped_cycle() > 0 else wm.time().cycle()
        current = val % len(candidate_unum)
        next = (val+1)%len(candidate_unum)

        self._current_sender_unum = candidate_unum[current]
        self._next_sender_unum = candidate_unum[next]

    def say_recovery(self, agent: 'PlayerAgent'):
        current_len = agent.effector().get_say_message_length()
        available_len = ServerParam.i().player_say_msg_size() - current_len
        if available_len < Messenger.SIZES[Messenger.Types.RECOVERY]:
            return False

        agent.add_say_message(RecoveryMessenger(agent.world().self().recovery()))
        log.sw_log().communication().add_text('(sample communication) say self recovery')
        return True


    def say_stamina(self, agent: 'PlayerAgent'):
        current_len = agent.effector().get_say_message_length()
        if current_len == 0:
            return False
        available_len = ServerParam.i().player_say_msg_size() - current_len
        if available_len < Messenger.SIZES[Messenger.Types.STAMINA]:
            return False
        agent.add_say_message(StaminaMessenger(agent.world().self().stamina()))
        log.sw_log().communication().add_text('(sample communication) say self stamina')
        return True

    def attention_to_someone(self, agent: 'PlayerAgent'): # TODO IMP FUNC
        wm = agent.world()
        ef = agent.effector()

        if wm.self().pos().x() > wm.offside_line_x() - 15. \
            and wm.intercept_table().self_reach_cycle() <= 3:
            if self._current_sender_unum != wm.self().unum() and self._current_sender_unum != UNUM_UNKNOWN:
                agent.do_attentionto(wm.our_side(), self._current_sender_unum)
                player = wm.our_player(self._current_sender_unum)
                if player is not None:
                    log.debug_client().add_circle(player.pos(), 3., color='#000088')
                    log.debug_client().add_line(player.pos(), wm.self().pos(), '#000088')
                log.debug_client().add_message(f'AttCurSender{self._current_sender_unum}')
            else:
                candidates: list[PlayerObject] = []
                for p in wm.teammates_from_self():
                    if p.goalie() or p.unum() == UNUM_UNKNOWN or p.pos().x() > wm.offside_line_x() + 1.:
                        continue
                    if p.dist_from_self() > 20.:
                        break

                    candidates.append(p)

                self_next = ef.queued_next_self_pos()

                target_teammate: PlayerObject = None
                max_x = -100000
                for p in candidates:
                    diff = p.pos() + p.vel() - self_next
                    x = diff.x() * (1. - diff.abs_y() / 40)
                    if x > max_x:
                        max_x = x
                        target_teammate = p

                if target_teammate is not None:
                    log.sw_log().communication().add_text(f'(attentionto someone) most front teammate')
                    log.debug_client().add_message(f'AttFrontMate{target_teammate.unum()}')
                    log.debug_client().add_circle(target_teammate.pos(), 3., color='#000088')
                    log.debug_client().add_line(target_teammate.pos(), wm.self().pos(), '#000088')
                    agent.do_attentionto(wm.our_side(), target_teammate.unum())
                    return

                if wm.self().attentionto_unum() > 0:
                    log.sw_log().communication().add_text('(attentionto someone) attentionto off. maybe ball owner')
                    log.debug_client().add_message('AttOffBOwner')
                    agent.do_attentionto_off()
            return

        fastest_teammate = wm.intercept_table().fastest_teammate()
        self_min = wm.intercept_table().self_reach_cycle()
        mate_min = wm.intercept_table().teammate_reach_cycle()
        opp_min = wm.intercept_table().opponent_reach_cycle()

        if fastest_teammate is not None \
            and fastest_teammate.unum() != UNUM_UNKNOWN \
            and mate_min <= 1 \
            and mate_min < self_min \
            and mate_min <= opp_min + 1 \
            and mate_min <= 5 + min(4, fastest_teammate.pos_count()) \
            and wm.ball().inertia_point(mate_min).dist2(ef.queued_next_self_pos()) < 35.**2:
            log.debug_client().add_message(f'AttBallOwner{fastest_teammate.unum()}')
            log.debug_client().add_circle(fastest_teammate.pos(), 3., color='#000088')
            log.debug_client().add_line(fastest_teammate.pos(), wm.self().pos(), '#000088')
            agent.do_attentionto(wm.our_side(), fastest_teammate.unum())
            return

        nearest_teammate = wm.get_teammate_nearest_to_ball(5)
        if nearest_teammate is not None \
            and nearest_teammate.unum() != UNUM_UNKNOWN \
            and opp_min <= 3 \
            and opp_min <= mate_min \
            and opp_min <= self_min \
            and nearest_teammate.dist_from_self() < 45. \
            and nearest_teammate.dist_from_ball() < 20.:
            log.debug_client().add_message(f'AttBallNearest(1){nearest_teammate.unum()}')
            log.debug_client().add_circle(nearest_teammate.pos(), 3., color='#000088')
            log.debug_client().add_line(nearest_teammate.pos(), wm.self().pos(), '#000088')
            agent.do_attentionto(wm.our_side(), nearest_teammate.unum())
            return

        if nearest_teammate is not None \
            and nearest_teammate.unum() != UNUM_UNKNOWN \
            and wm.ball().pos_count() >= 3 \
            and nearest_teammate.dist_from_ball() < 20.:
            log.debug_client().add_message(f'AttBallNearest(2){nearest_teammate.unum()}')
            log.debug_client().add_circle(nearest_teammate.pos(), 3., color='#000088')
            log.debug_client().add_line(nearest_teammate.pos(), wm.self().pos(), '#000088')
            agent.do_attentionto(wm.our_side(), nearest_teammate.unum())
            return

        if nearest_teammate is not None \
            and nearest_teammate.unum() != 45. \
            and nearest_teammate.dist_from_self() < 45. \
            and nearest_teammate.dist_from_ball() < 3.5:
            log.debug_client().add_message(f'AttBallNearest(3){nearest_teammate.unum()}')
            log.debug_client().add_circle(nearest_teammate.pos(), 3., color='#000088')
            log.debug_client().add_line(nearest_teammate.pos(), wm.self().pos(), '#000088')
            agent.do_attentionto(wm.our_side(), nearest_teammate.unum())
            return

        if self._current_sender_unum != wm.self().unum() and self._current_sender_unum != UNUM_UNKNOWN:
            log.debug_client().add_message(f'AttCurSender{self._current_sender_unum}')
            player = wm.our_player(self._current_sender_unum)
            if player is not None:
                log.debug_client().add_circle(player.pos(), 3., color='#000088')
                log.debug_client().add_line(player.pos(), wm.self().pos(), '#000088')
            agent.do_attentionto(wm.our_side(), self._current_sender_unum)
        else:
            log.debug_client().add_message(f'AttOff')
            agent.do_attentionto_off()




    def execute(self, agent: 'PlayerAgent'):
        if not team_config.USE_COMMUNICATION:
            return False

        self.update_current_sender(agent)

        wm = agent.world()
        penalty_shootout = wm.game_mode().is_penalty_kick_mode()

        say_recovery = False
        if wm.game_mode().type() == GameModeType.PlayOn \
                and not penalty_shootout \
                and self._current_sender_unum == wm.self().unum() \
                and wm.self().recovery() < ServerParam.i().recover_init() - 0.002:
            say_recovery = True
            self.say_recovery(agent)

        if wm.game_mode().type() == GameModeType.BeforeKickOff \
                or wm.game_mode().type().is_after_goal() \
                or penalty_shootout:
            return say_recovery

        if not(wm.game_mode().type() == GameModeType.BeforeKickOff or wm.game_mode().type().is_kick_off()):
            self.say_ball_and_players(agent)
        self.say_stamina(agent)

        self.attention_to_someone(agent)  # TODO IMP FUNC

        return True
