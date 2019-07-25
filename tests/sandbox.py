import math

from extutils import exec_timing_ns
from extutils.utils import to_snake_case


d = {i: None for i in range(500000)}


@exec_timing_ns
def wrap():
    for i in range(10000000):
        1 / math.pow(100, 1.4 - 1)


@exec_timing_ns
def wrap2():
    for i in range(10000000):
        100 / math.pow(100, 1.4)


if __name__ == "__main__":
    wrap()
    wrap2()
