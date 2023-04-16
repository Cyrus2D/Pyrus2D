from pyrusgeom.vector_2d import Vector2D

from lib.action.neck_body_to_point import NeckBodyToPoint
from lib.action.neck_turn_to_relative import NeckTurnToRelative
from lib.action.view_wide import ViewWide
from lib.debug.debug import log
from lib.player.soccer_action import BodyAction

from typing import TYPE_CHECKING

from lib.rcsc.types import ViewWidth

if TYPE_CHECKING:
    from lib.player.player_agent import PlayerAgent


class ScanField(BodyAction):
    def __init__(self):
        pass

    def execute(self, agent: 'PlayerAgent'):
        log.debug_client().add_message('ScanField/')
        wm = agent.world()
        if not wm.self().pos_valid():
            agent.do_turn(60.)
            agent.set_neck_action(NeckTurnToRelative(0))
            return True

        if wm.ball().pos_valid():
            self.scan_all_field(agent)
            return True
        self.find_ball(agent)
        return True

    def find_ball(self, agent: 'PlayerAgent'):
        wm = agent.world()

        if agent.effector().queued_next_view_width() is not ViewWidth.WIDE:
            agent.set_view_action(ViewWide())

        my_next = wm.self().pos() + wm.self().vel()
        face_angle = (wm.ball().seen_pos() - my_next).th() if wm.ball().seen_pos().is_valid() else (my_next*-1).th()

        search_flag = wm.ball().lost_count() //3
        if search_flag%2==1:
            face_angle += 180.

        face_point = my_next + Vector2D(r=10, a=face_angle)
        NeckBodyToPoint(face_point).execute(agent)

    def scan_all_field(self, agent: 'PlayerAgent'):
        wm = agent.world()
        if agent.effector().queued_next_view_width() is not ViewWidth.WIDE:
            agent.set_view_action(ViewWide())

        turn_moment=wm.self().view_width().width() + agent.effector().queued_next_view_width().width()
        turn_moment /= 2
        agent.do_turn(turn_moment)
        agent.set_neck_action(NeckTurnToRelative(wm.self().neck()))




























