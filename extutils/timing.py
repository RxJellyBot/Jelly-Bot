import time
import inspect
from dataclasses import dataclass
from typing import Any

from extutils.logger import LoggerSkeleton

__all__ = ["exec_timing", "exec_timing_ns", "exec_timing_result"]

exec_logger = LoggerSkeleton("utils.exectimer", logger_name_env="TIME_EXEC")


@dataclass
class ExecutionResult:
    return_: Any
    execution_ns: int
    caller_stack: inspect.FrameInfo

    @property
    def execution_us(self) -> float:
        return self.execution_ns / 1000

    @property
    def execution_ms(self) -> float:
        return self.execution_us / 1000

    def __repr__(self):
        return f"{self.execution_us:.2f} us - " \
               f"Line {self.caller_stack.lineno} {self.caller_stack.function} in {self.caller_stack.filename}"


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


def exec_timing_result(fn, *args, **kwargs) -> ExecutionResult:
    _start_ = time.time_ns()
    ret = fn(*args, **kwargs)

    exec_result = ExecutionResult(
        return_=ret, execution_ns=time.time_ns() - _start_, caller_stack=inspect.stack()[1])

    exec_logger.logger.info(exec_result)

    return exec_result
