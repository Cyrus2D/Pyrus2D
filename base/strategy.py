from lib.math.geom import *


class Strategy:
    def __init__(self):
        self._base_poses = []
        self._base_poses.append([Vector2D(-45, 0), 7, 10])
        self._base_poses.append([Vector2D(-30, -10), 7, 10])
        self._base_poses.append([Vector2D(-30, 10), 7, 10])
        self._base_poses.append([Vector2D(-30, -20), 7, 10])
        self._base_poses.append([Vector2D(-30, 20), 7, 10])
        self._base_poses.append([Vector2D(0, -15), 15, 15])
        self._base_poses.append([Vector2D(0, 15), 15, 15])
        self._base_poses.append([Vector2D(0, 0), 15, 15])
        self._base_poses.append([Vector2D(30, -15), 15, 15])
        self._base_poses.append([Vector2D(30, 15), 15, 15])
        self._base_poses.append([Vector2D(30, 0), 15, 15])
        self._poses = [Vector2D(0, 0) for i in range(11)]

    def update(self, ball_pos):
        for p in range(len(self._poses)):
            x = ball_pos.x() / 52.5 * self._base_poses[p - 1][1] + self._base_poses[p - 1][0].x()
            y = ball_pos.y() / 52.5 * self._base_poses[p - 1][1] + self._base_poses[p - 1][0].y()
            self._poses[p - 1] = Vector2D(x, y)

    def get_pos(self, unum):
        return self._poses[unum - 1]
