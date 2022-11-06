from lib.rcsc.game_time import GameTime
from lib.rcsc.types import ViewQuality, ViewWidth, SideID, Card, UNUM_UNKNOWN


class BodySensor:
    def __init__(self):
        self._current: GameTime = GameTime()

        self._view_quality: ViewQuality = ViewQuality(ViewQuality.ILLEGAL)
        self._view_width: ViewWidth = ViewWidth(ViewWidth.ILLEGAL)

        self._stamina: float = 0.
        self._effort: float = 0.
        self._stamina_capacity: float = 0.
        self._speed_mag: float = 0.
        self._speed_dir_relative: float = 0.
        self._neck_relative: float = 0.

        self._kick_count: int = 0
        self._dash_count: int = 0
        self._turn_count: int = 0
        self._say_count: int = 0
        self._turn_neck_count: int = 0
        self._catch_count: int = 0
        self._move_count: int = 0
        self._change_view_count: int = 0

        self._arm_movable: int = 0
        self._arm_expires: int = 0

        self._pointto_dist: float = 0
        self._pointto_dir: float = 0
        self._pointto_count: int = 0

        self._attentionto_side: SideID = SideID.NEUTRAL
        self._attentionto_unum: int = 0
        self._attentionto_count: int = 0

        self._tackle_expires: int = 0
        self._tackle_count: int = 0

        self._none_collided: bool = False
        self._ball_collided: bool = False
        self._player_collided: bool = False
        self._post_collided: bool = False

        self._charged_expires: int = 0
        self._card: Card = Card.NO_CARD

    def parse(self, msg: str, current_time: GameTime):
        self._current = current_time.copy()

        r = msg.split(' ')

        _sense_time = int(r[1].strip(')('))
        self._view_quality = ViewQuality(r[3].strip(')('))
        self._view_width = ViewWidth(r[4].strip(')('))
        self._stamina = float(r[6].strip(')('))
        self._effort = float(r[7].strip(')('))
        self._speed_mag = float(r[10].strip(')('))
        self._speed_dir_relative = float(r[11].strip(')('))
        self._neck_relative = float(r[13].strip(')('))
        self._kick_count = int(r[15].strip(')('))
        self._dash_count = int(r[17].strip(')('))
        self._turn_count = int(r[19].strip(')('))
        self._say_count = int(r[21].strip(')('))
        self._turn_neck_count = int(r[23].strip(')('))
        self._catch_count = int(r[25].strip(')('))
        self._move_count = int(r[27].strip(')('))
        self._change_view_count = int(r[29].strip(')('))
        self._arm_movable = int(r[32].strip(')('))
        self._arm_expires = int(r[34].strip(')('))
        self._pointto_dist = int(r[36].strip(')('))
        self._pointto_dir = int(r[37].strip(')('))
        self._pointto_count = int(r[39].strip(')('))

        attention_target = r[42].strip(')(')
        k = 0 if attention_target[0] == 'n' else 1

        self._attentionto_unum = UNUM_UNKNOWN
        if k > 0:
            self._attentionto_unum = int(r[43].strip(')('))

        self._attentionto_count = int(r[44 + k].strip(')('))

        self._tackle_expires = int(r[47 + k].strip(')('))
        self._tackle_count = int(r[49 + k].strip(')('))

        if attention_target == 'n':
            self._attentionto_side = SideID.NEUTRAL
        elif attention_target == 'l':
            self._attentionto_side = SideID.LEFT
        elif attention_target == 'r':
            self._attentionto_side = SideID.RIGHT
        else:
            print("Body_sensor: Failed to parse Attentionto")

        # Parse collision
        self._ball_collided = False
        self._none_collided = False
        self._post_collided = False
        self._player_collided = False


        col = msg[msg.find('(collision'): msg.find('foul')]
        if 'none' in col:
            self._none_collided = True
        else:
            if 'ball' in col:
                self._ball_collided = True
            if 'player' in col:
                self._player_collided = True
            if 'post' in col:
                self._post_collided = True


    def time(self) -> GameTime:
        return self._current

    def view_quality(self):
        return self._view_quality

    def view_width(self):
        return self._view_width

    def stamina(self):
        return self._stamina

    def effort(self):
        return self._effort

    def stamina_capacity(self):
        return self._stamina_capacity

    def speed_mag(self):
        return self._speed_mag

    def speed_dir(self):
        return self._speed_dir_relative

    def neck_relative(self):
        return self._neck_relative

    def kick_count(self):
        return self._kick_count

    def dash_count(self):
        return self._dash_count

    def turn_count(self):
        return self._turn_count

    def say_count(self):
        return self._say_count

    def turn_neck_count(self):
        return self._turn_neck_count

    def catch_count(self):
        return self._catch_count

    def move_count(self):
        return self._move_count

    def change_view_count(self):
        return self._change_view_count

    def arm_movable(self):
        return self._arm_movable

    def arm_expires(self):
        return self._arm_expires

    def pointto_dist(self):
        return self._pointto_dist

    def pointto_dir(self):
        return self._pointto_dir

    def pointto_count(self):
        return self._pointto_count

    def attentionto_side(self):
        return self._attentionto_side

    def attentionto_unum(self):
        return self._attentionto_unum

    def attentionto_count(self):
        return self._attentionto_count

    def tackle_expires(self):
        return self._tackle_expires

    def tackle_count(self):
        return self._tackle_count

    def none_collided(self):
        return self._none_collided

    def ball_collided(self):
        return self._ball_collided

    def player_collided(self):
        return self._player_collided

    def post_collided(self):
        return self._post_collided

    def charged_expires(self):
        return self._charged_expires

    def card(self):
        return self._card
