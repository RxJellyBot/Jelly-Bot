import time
import inspect

from extutils.logger import LoggerSkeleton

__all__ = ["exec_timing", "exec_timing_ns", "exec_logger"]


exec_logger = LoggerSkeleton("utils.exectimer", logger_name_env="TIME_EXEC")


def exec_timing(fn):
    def inner(*args, **kwargs):
        _start_ = time.time()
        ret = fn(*args, **kwargs)
        _duration_ = time.time() - _start_

        caller = inspect.stack()[1]

        exec_logger.logger.info(f"{_duration_ * 1000} ms - Line {caller.lineno} {caller.function} in {caller.filename}")

        return ret
    return inner


def exec_timing_ns(fn):
    def inner(*args, **kwargs):
        _start_ = time.time_ns()
        ret = fn(*args, **kwargs)
        _duration_ = time.time_ns() - _start_

        caller = inspect.stack()[1]

        exec_logger.logger.info(f"{_duration_} ns - Line {caller.lineno} {caller.function} in {caller.filename}")

        return ret
    return inner
