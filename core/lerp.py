import math

import arcade


def lerp(start, end, ratio):
    compare = start - end
    if compare == 0:
        return start
    else:
        if 0<= ratio <= 1:
            final = (ratio * start) + ((1 - ratio) * end)
        else:
            return None
        return final
