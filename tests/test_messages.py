from pyrusgeom.angle_deg import AngleDeg
from pyrusgeom.vector_2d import Vector2D

from lib.messenger.ball_goalie_messenger import BallGoalieMessenger
from lib.messenger.ball_messenger import BallMessenger
from lib.messenger.ball_player_messenger import BallPlayerMessenger
from lib.messenger.converters import MessengerConverter
from lib.messenger.goalie_messenger import GoalieMessenger
from lib.messenger.goalie_player_messenger import GoaliePlayerMessenger
from lib.messenger.messenger_memory import MessengerMemory
from lib.messenger.one_player_messenger import OnePlayerMessenger
from lib.messenger.recovery_message import RecoveryMessenger
from lib.messenger.stamina_messenger import StaminaMessenger
from lib.messenger.three_player_messenger import ThreePlayerMessenger
from lib.messenger.two_player_messenger import TwoPlayerMessenger
from lib.player.action_effector import ActionEffector
from lib.messenger.ball_pos_vel_messenger import BallPosVelMessenger
from lib.messenger.messenger import Messenger
from lib.player.object_player import PlayerObject
from lib.player.object_ball import BallObject
from lib.player.world_model import WorldModel
from lib.messenger.player_pos_unum_messenger import PlayerPosUnumMessenger
from lib.rcsc.game_time import GameTime
from lib.rcsc.types import SideID


def test():
    wm_sender = WorldModel()
    wm_reciever = WorldModel()

    wm_sender._our_side = 'l'
    wm_reciever._our_side = 'l'

    player = PlayerObject()
    player._pos = Vector2D(10, 20)
    player._unum = 5
    player._side = SideID.LEFT

    player2 = PlayerObject()
    player2._pos = Vector2D(1, 2)
    player2._unum = 5
    player2._side = SideID.LEFT
    player2._pos_count = 20
    player2._seen_pos_count = 20

    wm_sender._our_players_array[5] = player
    wm_sender._teammates.append(player)
    wm_reciever._teammates.append(player2)

    ball = BallObject()
    ball._pos = Vector2D(3, 4)
    ball._vel = Vector2D(2, -2)

    wm_sender._ball = ball

    ball2 = BallObject()
    ball2._pos = Vector2D(0, 0)
    ball2._vel = Vector2D(0, 0)

    ball2._pos_count = 10
    ball2._vel_count = 10

    wm_reciever._ball = ball2

    wm_sender._time = GameTime(10, 0)
    wm_reciever._time = GameTime(10, 0)
    wm_reciever._messenger_memory._time = GameTime(10)
    wm_reciever._messenger_memory._ball_time = GameTime(10)
    wm_reciever._messenger_memory._player_time = GameTime(10)

    print(wm_sender._teammates)
    print(wm_reciever._teammates)
    print(wm_sender._ball)
    print(wm_reciever._ball)

    msg = Messenger.encode_all(wm_sender, [PlayerPosUnumMessenger(5), BallPosVelMessenger()])

    Messenger.decode_all(wm_reciever._messenger_memory, msg, 4, wm_reciever.time())
    wm_reciever.update_ball_by_haer(ActionEffector())
    wm_reciever.update_players_by_hear()

    print(wm_sender._teammates)
    print(wm_reciever._teammates)
    print(wm_sender._ball)
    print(wm_reciever._ball)


def test2():
    cc = MessengerConverter([(-52.5, 52.5, 2 ** 10), (-34, 34, 2 ** 9), (-2.7, 2.7, 2 ** 6), (-2.7, 2.7, 2 ** 6)])
    w = cc.convert_to_word([3, 4, 2, -2])
    print(w)

    v = cc.convert_to_values(w)
    print(v)


def test3():
    cc = BallPlayerMessenger().CONVERTER

    data = [3, 4, 2, -2, 0, 10, -30, 40]
    msg = cc.convert_to_word(data)
    print(msg)

    val = cc.convert_to_values(msg)
    print(data)
    print(val)
    print([abs(v - d) for v, d in zip(val, data)])


def test_mm():
    gu = 1
    gp = Vector2D(40., 12)
    gb = AngleDeg(170)
    pu = 3
    pp = Vector2D(40., 33.9)

    mm = MessengerMemory()

    print(gu, gp, gb, pu, pp)
    msg = GoaliePlayerMessenger(gu, gp, gb, pu, pp).encode()
    print(msg)
    Messenger.decode_all(mm, msg, 3, GameTime(10))

    print(mm.players()[0].pos_)
    print(mm._goalie[0].pos_)


def test_mm2():
    u1 = 22
    p1 = Vector2D(-24.5, 0.6)
    u2 = 1
    p2 = Vector2D(-51.5, 2)
    u3 = 22
    p3 = Vector2D(52, 12)

    stamina = 1500

    mm = MessengerMemory()

    print(u1, p1, u2, p2, u3, p3, stamina)
    msg = Messenger.encode_all([TwoPlayerMessenger(u1, p1, u2, p2), StaminaMessenger(stamina)])
    print(msg)

    Messenger.decode_all(mm, msg, 3, GameTime(10))
    print(mm.players()[0].pos_)
    print(mm.players()[1].pos_)
    print(mm._stamina[0].rate_)


def test_one_player():
    unum = 1
    pos = Vector2D(-52., 30)
    print(unum, pos)
    msg = OnePlayerMessenger(unum, pos).encode()
    print(msg)

    print(OnePlayerMessenger.CONVERTER.convert_to_values(msg[1:]))


def test_two_player():
    u1 = 22
    p1 = Vector2D(-24.5, 0.6)
    u2 = 1
    p2 = Vector2D(-51.5, 2)
    print(u1, p1, u2, p2)
    msg = TwoPlayerMessenger(u1, p1, u2, p2).encode()
    print(msg)

    print(TwoPlayerMessenger.CONVERTER.convert_to_values(msg[1:]))


def test_three_player():
    u1 = 2 + 11
    p1 = Vector2D(5.441864657550282,-36.15640365877976)
    u2 = 3 + 11
    p2 = Vector2D(9.548082361799027,-37.26023761462523)
    u3 = 4 + 11
    p3 = Vector2D(12.174446180516131, -10.985076789602786)
    print(u1, p1, u2, p2, u3, p3)
    msg = ThreePlayerMessenger(u1, p1, u2, p2, u3, p3).encode()
    print(msg)

    print(ThreePlayerMessenger.CONVERTER.convert_to_values(msg[1:]))


def test_goalie_messenger():
    gu = 1
    gp = Vector2D(40., 12)
    gb = AngleDeg(170)

    print(gu, gp, gb)
    msg = GoalieMessenger(gu, gp, gb).encode()
    print(msg)
    print(GoalieMessenger.CONVERTER.convert_to_values(msg[1:]))


def test_ball_goalie_messenger():
    bp = Vector2D(12, 30)
    bv = Vector2D(1, -1)
    gp = Vector2D(40., 33.9)
    gb = AngleDeg(170)

    print(bp, bv, gp, gb)
    msg = BallGoalieMessenger(bp, bv, gp, gb).encode()
    print(BallGoalieMessenger.CONVERTER.convert_to_values(msg[1:]))


def test_ball_messenger():
    bp = Vector2D(12, 30)
    bv = Vector2D(1, -1)

    print(bp, bv)
    msg = BallMessenger(bp, bv).encode()
    print(BallMessenger.CONVERTER.convert_to_values(msg[1:]))


def test_ball_player_messenger():
    bp = Vector2D(0, 0)
    bv = Vector2D(0, 0)
    pu = 10
    pp = Vector2D(-9.15, 10.5)
    pb = AngleDeg(2.1)

    print(bp, bv, pu, pp, pb)
    msg = BallPlayerMessenger(bp, bv, pu, pp, pb).encode()
    print(msg)

    print(BallPlayerMessenger.CONVERTER.convert_to_values(msg[1:]))


def test_goalie_player_messenger():
    gu = 1
    gp = Vector2D(40., 12)
    gb = AngleDeg(170)
    pu = 3
    pp = Vector2D(40., 33.9)

    print(gu, gp, gb, pu, pp)
    msg = GoaliePlayerMessenger(gu, gp, gb, pu, pp).encode()
    print(msg)
    print(GoaliePlayerMessenger.CONVERTER.convert_to_values(msg[1:]))


def test_recovery_messenger():
    recovery = 0.99

    print(recovery)
    msg = RecoveryMessenger(recovery).encode()
    print(msg)
    print(RecoveryMessenger.CONVERTER.convert_to_values(msg[1:]))


def test_stamina_messenger():
    stamina = 5000

    print(stamina)
    msg = StaminaMessenger(stamina).encode()
    print(msg)
    print(StaminaMessenger.CONVERTER.convert_to_values(msg[1:]))


if __name__ == "__main__":
    test_ball_player_messenger()
