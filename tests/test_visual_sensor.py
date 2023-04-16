from lib.player.sensor.visual_sensor import SeeParser
from lib.rcsc.game_time import GameTime
from lib.debug.debug_print import debug_print

message = '(see 245 ((f c) 15.5 2 0 1.3) ((f c b) 48.9 16) ((f r t) 60.9 -86) ((f r b) 75.2 -27) ((f l b) 67.4 67) ((f g r b) 61.6 -47) ((g r) 59.7 -53) ((f g r t) 58.6 -60) ((f g l b) 51.9 88) ((f p r b) 54.1 -27) ((f p r c) 43.8 -48) ((f p r t) 41.7 -75) ((f p l b) 46.5 64) ((f p l c) 33.8 87) ((f b 0) 54.1 17) ((f b r 10) 55.7 7) ((f b r 20) 59.1 -3) ((f b r 30) 64.1 -11) ((f b r 40) 70.1 -18) ((f b r 50) 76.7 -23) ((f b l 10) 53.5 28) ((f b l 20) 55.7 38) ((f b l 30) 59.1 47) ((f b l 40) 64.1 55) ((f b l 50) 69.4 62) ((f r 0) 64.7 -54) ((f r t 10) 62.8 -63) ((f r t 20) 62.8 -72) ((f r t 30) 64.7 -81) ((f r b 10) 67.4 -46) ((f r b 20) 71.5 -39) ((f r b 30) 76.7 -32) ((f l b 10) 57.4 87) ((f l b 20) 62.8 79) ((f l b 30) 68.7 72) ((b) 33.1 -81 0.662 0.9) ((p "HELIOS_base" 3) 12.2 17 0 1.2 -104 -50) ((p "HELIOS_base") 27.1 6 -131) ((p "HELIOS_base" 6) 18.2 -56 0 0.4 -67 -152) ((p "HELIOS_base" 8) 30 -37 0 0.2 -67 22) ((p "HELIOS_base") 30 -84) ((p "HELIOS_base") 40.4 -17) ((p "HELIOS_base" 11) 22.2 -60 0 0.3 -64 -59) ((p) 54.6 -57) ((p "col") 30 -26) ((p "col" 3) 24.5 -42 -0 0.6 -133 -132) ((p "col" 4) 33.1 -5 -0 0.6 152 -148) ((p "col" 5) 16.4 -62 -0.328 0.5 -108 -107) ((p "col" 6) 18.2 -14 -0 1 -122 -122) ((p "col" 7) 22.2 7 0 0.9 -163 -156) ((p "col" 8) 10 -17 -0.2 1.8 -174 -109) ((p "col") 36.6 12) ((p "col" 11) 16.4 1 0 1.2 -62 -152) ((l b) 52.5 -67))'

vs = SeeParser()
vs.parse(message, "HELIOS_base", GameTime(-1, -1))


debug_print(vs)