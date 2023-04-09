from pyrusgeom.geom_2d import *
from lib.debug.color import Color
from lib.debug.debug import log
from lib.rcsc.server_param import ServerParam as SP
from base.generator_action import KickAction, KickActionType, BhvKickGen
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.player.world_model import WorldModel

debug_clear_ball = True


class BhvClearGen(BhvKickGen):
    def generator(self, wm: 'WorldModel'):
        log.sw_log().clear().add_text("=========start clear ball generator")
        self.generate_clear_ball(wm)
        log.sw_log().clear().add_text("=========generated clear ball actions:")
        for candid in self.candidates:
            log.sw_log().clear().add_text(f'{candid.index} {candid.target_ball_pos} {candid.eval}')
        if debug_clear_ball:
            for candid in self.debug_list:
                if candid[2]:
                    log.sw_log().clear().add_message(candid[1].x(), candid[1].y(), '{}'.format(candid[0]))
                    log.sw_log().clear().add_circle(circle=Circle2D(candid[1], 0.2), color=Color(string='green'))
                else:
                    log.sw_log().clear().add_message(candid[1].x(), candid[1].y(), '{}'.format(candid[0]))
                    log.sw_log().clear().add_circle(circle=Circle2D(candid[1], 0.2), color=Color(string='red'))
        return self.candidates

    def add_to_candidate(self, wm: 'WorldModel', ball_pos: Vector2D):
        action = KickAction()
        action.target_ball_pos = ball_pos
        action.start_ball_pos = wm.ball().pos()
        action.start_ball_speed = 2.5
        action.type = KickActionType.Clear
        action.index = self.index

        action.eval = 0
        if ball_pos.x() > SP.i().pitch_half_length():
            action.eval = 200.0
        elif ball_pos.x() < -SP.i().pitch_half_length():
            if ball_pos.abs_y() < 10:
                action.eval = -200.0
            else:
                action.eval = -80.0
        elif ball_pos.abs_y() > SP.i().pitch_half_width():
            action.eval = ball_pos.x()
        elif ball_pos.x() < -30 and ball_pos.abs_y() < 20:
            action.eval = -100.0
        else:
            action.eval = ball_pos.dist(Vector2D(-SP.i().pitch_half_length(), 0.0))
        self.candidates.append(action)
        self.debug_list.append((self.index, ball_pos, True))
        self.index += 1

    def generate_clear_ball(self, wm: 'WorldModel'):
        angle_div = 16
        angle_step = 360.0 / angle_div

        for a in range(angle_div):
            ball_pos = wm.ball().pos()
            angle = AngleDeg(a * angle_step)
            speed = 2.5
            log.sw_log().clear().add_text(f'========= a:{a} speed:{speed} angle:{angle} ball:{ball_pos}')
            for c in range(30):
                ball_pos += Vector2D.polar2vector(speed, angle)
                log.sw_log().clear().add_text(f'--->>>{ball_pos}')
                speed *= SP.i().ball_decay()
                if ball_pos.x() > SP.i().pitch_half_length():
                    break
                if ball_pos.x() < -SP.i().pitch_half_length():
                    break
                if ball_pos.abs_y() > SP.i().pitch_half_width():
                    break
                receiver_opp = 0
                for opp in wm.opponents():
                    if not opp:
                        continue
                    if opp.unum() <= 0:
                        continue
                    opp_cycle = opp.pos().dist(ball_pos) / opp.player_type().real_speed_max() - opp.player_type().kickable_area()
                    opp_cycle -= min(0, opp.pos_count())
                    if opp_cycle <= c:
                        receiver_opp = opp.unum()
                        break
                if receiver_opp != 0:
                    break
            self.add_to_candidate(wm, ball_pos)

