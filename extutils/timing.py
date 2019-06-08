import time
from typing import Any


def exec_timing(fn, *args, **kwargs) -> (float, Any):
    _start = time.time()
    ret = fn(*args, **kwargs)
    _duration = time.time() - _start

    return _duration, ret
