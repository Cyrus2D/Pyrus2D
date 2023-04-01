from math import ceil
from typing import Union

from pyrusgeom.soccer_math import bound

from lib.debug.debug import log

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ().+-*/?<>_0123456789"


class MessengerConverter:
    def __init__(self, size, min_max_sizes: list[tuple[float, float, int]]):
        self._min_max_sizes = min_max_sizes
        self._size = size

    def convert_to_word(self, values):
        s = 0
        for i, (min_v, max_v, size) in enumerate(self._min_max_sizes):
            v = values[i]
            log.os_log().debug(f'v={v}')
            v = bound(min_v, v, max_v)
            v -= min_v
            v /= max_v - min_v
            v *= size

            s *= size
            s += int(v)

        n_chars = len(chars)
        words = []
        while s != 0:
            # print(s)
            words.append(s % n_chars)
            s = s // n_chars
            log.os_log().debug(f's={s}')
        # print(s)
        # words.append(s)
        msg = ''
        for word in words:
            msg += chars[word]

        while len(msg) < self._size-1:
            msg += chars[0]

        return msg

    def convert_to_values(self, msg):
        if msg == '':
            return None

        msg = msg[::-1]

        n_chars = len(chars)
        digit = len(msg) - 1

        val: int = 0

        for c in msg:
            i = chars.find(c)
            val += i * int(n_chars ** digit)
            digit -= 1

        values = []
        for i, (min_v, max_v, size) in enumerate(self._min_max_sizes[::-1]):
            v = val % size
            v = v / size * (max_v - min_v)
            v = v + min_v

            values.append(v)
            val = int(val / size)
        return values[::-1]


def convert_to_bits(values_min_max_sizes: list[tuple[float, float, float, int]]):
    s = 0
    for i, (v, min_v, max_v, size) in enumerate(values_min_max_sizes):
        v -= min_v
        v /= max_v - min_v
        v *= size

        s += int(v)

        print(f'{int(v)}, {s}', end=', ')
        if i != len(values_min_max_sizes) - 1:
            s *= values_min_max_sizes[i + 1][-1]
        print(s)
    return s


#  bYl)0L

def convert_to_words(val: int, size: int) -> str:
    n_chars = len(chars)
    words = []
    for _ in range(size - 1):
        words.append(val % n_chars)
        val = val // n_chars

    words.append(val)
    msg = ''
    for word in words:
        msg += chars[word]

    return msg


def convert_to_int(msg: str) -> Union[int, None]:
    if msg == '':
        return None

    msg = msg[::-1]

    n_chars = len(chars)
    digit = len(msg) - 1

    val: int = 0

    for c in msg:
        i = chars.find(c)
        val += i * int(n_chars ** digit)
        digit -= 1

    return val
