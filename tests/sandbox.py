from extutils import exec_timing

import pytz
from datetime import datetime


def wrap():
    for i in range(50000000):
        sign = "+" if i > 0 else "-"
        sign + str(i)


def wrap2():
    for i in range(50000000):
        f"{i:+d}"


if __name__ == "__main__":
    duration, ret = exec_timing(wrap)
    print(f"Duration: {duration}s")
    duration, ret = exec_timing(wrap)
    print(f"Duration: {duration}s")
    duration, ret = exec_timing(wrap)
    print(f"Duration: {duration}s")
    duration, ret = exec_timing(wrap2)
    print(f"Duration: {duration}s")
    duration, ret = exec_timing(wrap2)
    print(f"Duration: {duration}s")
    duration, ret = exec_timing(wrap2)
    print(f"Duration: {duration}s")
