import time
from typing import Any


def exec_timing(fn):
    def inner(*args, **kwargs):
        _start_ = time.time()
        ret = fn(*args, **kwargs)
        _duration_ = time.time() - _start_

        print(f"Duration: {_duration_} ns")

        return ret
    return inner


def exec_timing_ns(fn):
    def inner(*args, **kwargs):
        _start_ = time.time_ns()
        ret = fn(*args, **kwargs)
        _duration_ = time.time_ns() - _start_

        print(f"Duration: {_duration_} ns")

        return ret
    return inner
