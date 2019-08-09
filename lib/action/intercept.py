from lib.action.go_to_point import GoToPoint
from lib.action.intercept_info import InterceptInfo
from lib.math.vector_2d import Vector2D
from lib.player.templates import PlayerAgent, WorldModel
from lib.rcsc.server_param import ServerParam


class Intercept:
    def __init__(self, save_recovery: bool = True,
                 face_point: Vector2D = Vector2D.invalid()):
        self._save_recovery = save_recovery
        self._face_point = face_point

    def execute(self, agent: PlayerAgent):
        wm = agent.world()

        if self.do_kickable_opponent_check(agent):
            return True

        table = wm.intercept_table()
        if table.self_reach_cycle() > 100:
            final_point = wm.ball().inertia_final_point()
            GoToPoint(final_point,
                      2,
                      ServerParam.i().max_dash_power()).execute(agent)
            return True

        best_intercept: InterceptInfo = self.get_best_intercept(wm, table)
        target_point = wm.ball().inertia_point(best_intercept.reach_cycle())
        if best_intercept.dash_cycle() == 0:
            face_point = self._face_point.copy()
            if not face_point.is_valid():
                face_point.assign(50.5, wm.self().pos().y() * 0.75)

            TurntoPoint(face_point,
                        best_intercept.reach_cycle()).execute(agent)
            return True

        if best_intercept.turn_cycle() > 0:
            my_inertia = wm.self().inertia_point(best_intercept.reach_cycle())
            target_angle = (target_point - my_inertia).th()
            if best_intercept.dash_power() < 0:
                target_angle -= 180

            return agent.do_turn(target_angle - wm.self().body())

        if self.do_wait_turn(agent, target_point, best_intercept):
            return True

        if self._save_recovery and not wm.self().stamina_model().capacity_is_empty():
            consumed_stamina = best_intercept.dash_power()
            if best_intercept.dash_power() < 0:
                consumed_stamina *= -2

            if (wm.self().stamina() - consumed_stamina
                    < ServerParam.i().recover_dec_thr_value() + 1)
                agent.do_turn(0)
                return False

        return self.do_inertia_dash(agent,
                                    target_point,
                                    best_intercept)
