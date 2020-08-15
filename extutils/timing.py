"""Utilities to time the function execution."""
import time
import inspect
from dataclasses import dataclass
from typing import Any

from extutils.logger import LoggerSkeleton

__all__ = ("exec_timing", "exec_timing_ns", "exec_timing_result",)

exec_logger = LoggerSkeleton("utils.exectimer", logger_name_env="TIME_EXEC")


@dataclass
class ExecutionResult:
    """Function execution result wrapper class."""

    return_: Any
    execution_ns: int
    caller_stack: inspect.FrameInfo

    @property
    def execution_us(self) -> float:
        """
        Get the time spent on the execution in microseconds (us).

        :return: time spent on the execution in us
        """
        return self.execution_ns / 1000

    @property
    def execution_ms(self) -> float:
        """
        Get the time spent on the execution in milliseconds (ms).

        :return: time spent on the execution in ms
        """
        return self.execution_us / 1000

    def __repr__(self):
        return f"{self.execution_us:.2f} us - " \
               f"Line {self.caller_stack.lineno} {self.caller_stack.function} in {self.caller_stack.filename}"


def exec_timing(fn):
    """
    Time the function execution and log it to ``utils.exectimer`` (level: ``logging.INFO``).

    The unit of the execution time is **milliseconds (ms)**.

    Usage:

    >>> @exec_timing
    >>> def func(num):
    >>>     # code goes here

    :param fn: function to be timed
    """

    def _inner(*args, **kwargs):
        _start_ = time.time()
        ret = fn(*args, **kwargs)
        _duration_ = time.time() - _start_

        caller = inspect.stack()[1]

        exec_logger.logger.info("%.3f ms - Line %d %s in %s",
                                _duration_ * 1000, caller.lineno, caller.function, caller.filename)

        return ret

    return _inner


def exec_timing_ns(fn):
    """
    Time the function execution and log it to ``utils.exectimer`` (level: ``logging.INFO``).

    The unit of the execution time is **nanoseconds (ns)**.

    Usage:

    >>> @exec_timing_ns
    >>> def func(num):
    >>>     # code goes here

    :param fn: function to be timed
    """

    def _inner(*args, **kwargs):
        _start_ = time.time_ns()
        ret = fn(*args, **kwargs)
        _duration_ = time.time_ns() - _start_

        caller = inspect.stack()[1]

        exec_logger.logger.info("%d ns - Line %d %s in %s",
                                _duration_, caller.lineno, caller.function, caller.filename)

        return ret

    return _inner


def exec_timing_result(fn, *args, log: bool = True, **kwargs) -> ExecutionResult:
    """
    Time the function execution and returns a result body :class:`ExecutionResult`.

    If ``log`` is ``True``, also log it to ``utils.exectimer`` (level: ``logging.INFO``).

    Usage:

    >>> def func(num):
    >>>     # code to be timed
    >>>
    >>> def main():
    >>>     result = exec_timing_result(func, 7)

    :param fn: function to be timed
    :param log: if the execution result should be logged
    :param args: args for `fn`
    :param kwargs: kwargs for `fn`
    """
    _start_ = time.time_ns()
    ret = fn(*args, **kwargs)

    exec_result = ExecutionResult(
        return_=ret, execution_ns=time.time_ns() - _start_, caller_stack=inspect.stack()[1])

    if log:
        exec_logger.logger.info(exec_result)

    return exec_result
