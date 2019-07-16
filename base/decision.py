from lib.action.go_to_point import *
from base.strategy import *

def get_decision(agent):
    agent.debug(f"time: {agent.world().time()}")
    st = Strategy()
    wm = agent.world()
    st.update(agent.world().ball().pos())
    target = st.get_pos(agent.world().self().unum())
    min_dist_ball = 1000
    nearest_tm = 0
    for u in range(1,12):
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
