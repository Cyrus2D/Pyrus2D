from lib.action.go_to_point import *
from base.strategy import *
from lib.debug.logger import *


def get_decision(agent):
    st = Strategy()
    wm: WorldModel = agent.world()
    dlog.add_line(Level.BLOCK, start=wm.self().pos(), end=wm.ball().pos(), color=Color(string="black"))
    dlog.add_text(Level.BLOCK, f"Test {wm.self().pos()}") # Aref come on :))) # HA HA HA HA :D
    dlog.add_circle(cicle=Circle2D(wm.self().pos(), 3), color=Color(string="blue"))
    st.update(agent.world().ball().pos())
    target = st.get_pos(agent.world().self().unum())
    min_dist_ball = 1000
    nearest_tm = 0
    for u in range(1, 12):
        tm = wm.our_player(u)
        if tm.unum() is not 0:
            dist = tm.pos().dist(wm.ball().pos())
            if dist < min_dist_ball:
                min_dist_ball = dist
                nearest_tm = u
    if nearest_tm == wm.self().unum():
        target = wm.ball().pos()
    GoToPoint(target, 2, 100).execute(agent)
    return True
