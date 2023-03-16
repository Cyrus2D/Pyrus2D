from math import exp

from pyrusgeom.soccer_math import bound

import team_config
from lib.debug.debug import log
from lib.messenger.ball_pos_vel_messenger import BallPosVelMessenger
from lib.messenger.messenger import Messenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.rcsc.game_time import GameTime
from lib.rcsc.server_param import ServerParam
from lib.rcsc.types import UNUM_UNKNOWN, GameModeType, SideID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent
    from lib.player.object_player import PlayerObject


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
            angle_diff = abs(wm.ball().vel().th() - wm.prev_ball().vel().th())

            log.sw_log().communication(f'(sample communication)'
                                       f'prev vel={wm.prev_ball().vel()}, r={prev_ball_speed}'
                                       f'current_vel={wm.ball().vel()}, r={wm.ball().vel()}')

            if current_ball_speed > prev_ball_speed + 0.1 \
                    or (
                    prev_ball_speed > 0.5 and current_ball_speed < prev_ball_speed * ServerParam.i().ball_decay() / 2) \
                    or (prev_ball_speed > 0.5 and angle_diff > 20.):
                log.sw_log().communication(f'(sample communication) ball vel changed')
                ball_vel_changed = True

        if wm.self().is_kickable():
            if ball_vel_changed and wm.last_kicker_side() != wm.our_side() and not wm.kickable_opponent():
                log.sw_log().communication().add_text(
                    "(sample communication) ball vel changed. opponent kicked. no opponent kicker")
                return True
            if ef.queued_next_ball_kickable() and current_ball_speed < 1.:  # TODO IMP FUNC
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

    def say_ball_and_players(self, agent: 'PlayerAgent'):
        SP = ServerParam.i()
        wm = agent.world()
        ef = agent.effector()

        current_len = ef.get_say_message_len()  # TODO IMP FUNC

        should_say_ball = self.should_say_ball(agent)
        should_say_goalie = self.should_say_opponent_goalie(agent)  # TODO IMP FUNC
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

        for p in mm.player_record():  # TODO IMP FUNC
            n = p[1].unum_
            if not (1 <= n <= 22):
                continue

            objects[n].score = wm.time().cycle() - p[0].cycle()

        if 1 <= wm.their_goalie_unum() <= 11:
            n = wm.their_goalie_unum() + 11
            diff = wm.time().cycle() - mm.goalie_time().cycle()  # TODO IMP FUNC
            objects[n].score = min(objects[n].score, diff)

        if wm.self().is_kickable():
            if ef.queued_next_ball_kickable():  # TODO IMP FUNC
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
                objects[i] = -1000
            else:
                d = (((p.pos().x() - ball_pos.x()) * x_rate) ** 2 + ((p.pos().y() - ball_pos.y()) * y_rate) ** 2) ** 0.5
                objects[i].score *= exp(-d ** 2 / (2 * variance ** 2))
                objects[i].score *= 0.3 ** p.unum_count()
                objects[i].player = p

            p = wm.their_player(i)
            if p is None or p.unum_count() >= 2:
                objects[i + 11] = -1000
            else:
                d = (((p.pos().x() - ball_pos.x()) * x_rate) ** 2 + ((p.pos().y() - ball_pos.y()) * y_rate) ** 2) ** 0.5
                objects[i + 11].score *= exp(-d ** 2 / (2 * variance ** 2))
                objects[i + 11].score *= 0.3 ** p.unum_count()
                objects[i + 11].player = p

        objects = list(filter(lambda x: x.score < 0.1, objects))
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
            Messenger.Types.BALL_POS_VEL_MESSAGE]:
            if available_len >= Messenger.SIZES[Messenger.Types.BALL_PLAYER]:  # TODO IMP FUNC
                agent.add_say_message(BallPlayerMessage(ef.queued_next_ball_pos(),  # TODO IMP FUNC
                                                        ball_vel,
                                                        wm.self().unum(),
                                                        ef.queued_next_self_pos(),
                                                        ef.queued_next_self_body()))
                self.update_player_send_time(wm, wm.our_side(), wm.self().unum())  # TODO IMP FUNC
            else:
                agent.add_say_message(BallMessageMessenger(ef.queued_next_ball_pos(), ball_vel))  # TODO IMP FUNC

            self._ball_send_time = wm.time().copy()
            log.sw_log().communication().add_text('(sample communication) only ball')
            return True

        if send_ball_and_player:
            if should_say_goalie and available_len >= Messenger.SIZES[Messenger.Types.BALL_GOALIE]:
                goalie = wm.get_their_goalie()  # TODO IMP FUNC
                agent.add_say_message(BallGoalieMessageMessenger(ef.queued_next_ball_pos(),  # TODO IMP FUNC
                                                                 ball_vel,
                                                                 goalie.pos() + goalie.vel(),
                                                                 goalie().vel()))
                self._ball_send_time = wm.time().copy()
                self.update_player_send_time(wm, goalie.side(), goalie.unum())  # TODO IMP FUNC

                log.sw_log().communication().add_text('(sample communication) ball and goalie')
                return True

            if available_len >= Messenger.SIZES[Messenger.Types.BALL_PLAYER]:
                p = send_players[0].player
                if p.unum() == wm.self().unum():
                    agent.add_say_message(BallPlayerMessageMessenger(ef.queued_next_ball_pos(),  # TODO IMP FUNC
                                                                     ball_vel,
                                                                     wm.self().unum(),
                                                                     ef.queued_next_self_pos(),
                                                                     ef.queued_next_self_body()))
                else:
                    agent.add_say_message(BallPlayerMessageMessenger(ef.queued_next_ball_pos(),  # TODO IMP FUNC
                                                                     ball_vel,
                                                                     send_players[0].number,
                                                                     p.pos() + p.vel(),
                                                                     p.body()))

                self._ball_send_time = wm.time().copy()
                self.update_player_send_time(wm, p.side(), p.unum())

                log.sw_log().communication().add_text(f'(sample communication) ball and player {p.side()}{p.unum()}')
                return True

        if wm.ball().pos().x() > 34 and wm.ball().pos().abs_y() < 20:
            goalie: PlayerObject = wm.get_their_goalie()  # TODO IMP FUNC

            if goalie is not None \
                    and goalie.seen_pos_count() == 0 \
                    and goalie.body_count() == 0 \
                    and goalie.pos().x() > 53. - 16 \
                    and goalie.pos().abs_y() < 20. \
                    and goalie.unum() != UNUM_UNKNOWN \
                    and goalie.dist_from_self() < 25:
                if available_len >= Messenger.SIZES[Messenger.Types.GOALIE_AND_PLAYER]:
                    player: PlayerObject = None
                    for p in send_players:
                        if p.player.unum() != goalie.unum() and p.player.side() != goalie.side()
                            player = p.player
                            break

                    if player is not None:
                        goalie_pos = goalie.pos() + goalie.vel()
                        goalie_pos.assign(
                            bound(53. - 16., goalie_pos.x(), 52.9),
                            bound(-20, goalie_pos.y(), 20),
                        )
                        agent.add_say_message(GoaliePlayerMessageMessenger(goalie.unum(),  # TODO IMP FUNC
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
                    agent.add_say_message(GoalieMessageMessenger(goalie.unum(),  # TODO IMP FUNC
                                                                 goalie_pos,
                                                                 goalie.body()))
                    self._ball_send_time = wm.time().copy()
                    self._opponent_send_time[goalie.unum()] = wm.time().copy()

                    log.sw_log().communication().add_text(f'(sample communication) say goalie info:'
                                                          f'{goalie.unum()} {goalie.pos()} {goalie.body()}')
                    return True

        if len(send_players) >= 3 and available_len >= Messenger.SIZES[Messenger.Types.THREE_PLAYERS]:
            p0 = send_players[0].player
            p1 = send_players[1].player
            p2 = send_players[2].player

            agent.add_say_message(ThreePlayerMessageMessenger(send_players[0].number,  # TODO IMP FUNC
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

        if len(send_players) >= 2 and available_len >= Messenger.Types[Messenger.Types.TWO_PLAYERS]:
            p0 = send_players[0].player
            p1 = send_players[1].player

            agent.add_say_message(TwoPlayerMessageMessenger(send_players[0].number,  # TODO IMP FUNC
                                                            p0.pos() + p0.vel(),
                                                            send_players[1].number,
                                                            p1.pos() + p1.vel()))
            self.update_player_send_time(wm, p0.side(), p0.unum())
            self.update_player_send_time(wm, p1.side(), p1.unum())

            log.sw_log().communication().add_text(f'(sample communication) two players:'
                                                  f'{p0.side()}{p0.unum()}'
                                                  f'{p1.side()}{p1.unum()}')
            return True

        if len(send_players) >= 1 and available_len >= Messenger.Types[Messenger.Types.GOALIE]:
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
                agent.add_say_message(GoalieMessageMessenger(p0.unum(),  # TODO IMP FUNC
                                                             goalie_pos,
                                                             p0.body()))

                self.update_player_send_time(wm, p0.side(), p0.unum())

                log.sw_log().communication().add_text(f'(sample communication) goalie:'
                                                      f'{p0.side()}{p0.unum()}')
                return True

        if len(send_players) >= 1 and available_len >= Messenger.Types[Messenger.Types.ONE_PLAYERS]:
            p0 = send_players[0].player

            agent.add_say_message(OnePlayerMessageMessenger(send_players[0].number,  # TODO IMP FUNC
                                                            p0.pos() + p0.vel()))

            self.update_player_send_time(wm, p0.side(), p0.unum())

            log.sw_log().communication().add_text(f'(sample communication) one player:'
                                                  f'{p0.side()}{p0.unum()}')
            return True

        return False

    def execute(self, agent: 'PlayerAgent'):
        if not team_config.USE_COMMUNICATION:  # TODO IMP FUNC
            return False

        self.update_current_sender(agent)  # TODO IMP FUNC

        wm = agent.world()
        penalty_shootout = wm.game_mode().is_penalty_kick_mode()

        say_recovery = False
        if wm.game_mode().type() == GameModeType.PlayOn \
                and not penalty_shootout \
                and self._current_sender_unum == wm.self().unum() \
                and wm.self().recovery() < ServerParam.i().recover_init() - 0.002:
            say_recovery = True
            self.say_recovery(agent)  # TODO IMP FUNC

        if wm.game_mode().type() == GameModeType.BeforeKickOff \
                or wm.game_mode().type().is_after_goal() \
                or penalty_shootout:
            return say_recovery

        self.say_ball_and_players(agent)  # TODO IMP FUNC
        self.say_stamina(agent)  # TODO IMP FUNC

        self.attention_to_someone(agent)  # TODO IMP FUNC

        return True
