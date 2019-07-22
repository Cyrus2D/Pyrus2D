"""
  \ file soccer_math
  \ brief math utility depending on RCSSServer2D

"""

from lib.math.geom import *

SERVER_EPS = 1.0e-10

"""
  \ brief calculate kick rate
  \ param dist distance from player to ball
  \ param dir_diff angle difference from player's body to ball
  \ param kprate player's kick power rate parameter
  \ param bsize ball radius
  \ param psize player radius
  \ param kmargin player's kickable area margin
  \ return rate of the kick power effect

"""


def kick_rate(dist: float, dir_diff: float, kprate: float, bsize: float, psize: float, kmargin: float):
    return kprate * (1.0
                     - 0.25 * math.fabs(dir_diff) / 180.0
                     - 0.25 * (dist - bsize - psize) / kmargin)
