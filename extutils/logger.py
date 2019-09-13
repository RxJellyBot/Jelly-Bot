import os
import sys
import logging

from extutils import split_fill

__all__ = ["LoggerSkeleton"]


LOGGER_SPLITTOR = ","
LOGGER_LVSPLIT = "|"


loggers = {}
if "LOGGER" in os.environ:
    for lgr in os.environ["LOGGER"].split(LOGGER_SPLITTOR):
        logger_name, lv = split_fill(lgr.strip(), 2, LOGGER_LVSPLIT)
        loggers[logger_name] = int(lv) if lv else lv


class GlobalLogFormatter(logging.Formatter):
    default_msec_format = "%s.%03d"


class GlobalLogHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(sys.stdout)


class LoggerSkeleton:
    DEFAULT_FMT = "%(asctime)s %(name)s[%(levelname)s]: %(message)s"

    def __init__(self, name: str, fmt: str = None, level: int = None, logger_name_env: str = None):
        # https://docs.python.org/3/library/logging.html#logrecord-attributes

        if not logger_name_env:
            logger_name_env = name

        self._enabled = False
        self._is_debug = bool(int(os.environ.get("DEBUG", 0)))

        if not level:
            if self._is_debug:
                level = logging.DEBUG
            elif "LOG_LEVEL" in os.environ:
                level = int(os.environ["LOG_LEVEL"])
            elif logger_name_env in loggers and loggers[logger_name_env]:
                level = loggers[logger_name_env]
            else:
                level = logging.WARNING

        self._is_debug = self._is_debug or level <= logging.DEBUG

        # Initialize objects
        self._fmt = GlobalLogFormatter(fmt if fmt else LoggerSkeleton.DEFAULT_FMT)
        self._handler = GlobalLogHandler()
        self._core = logging.getLogger(name)

        # Configs
        self.set_level(level)
        self._handler.setFormatter(self._fmt)

        # Activate
        if logger_name_env in loggers or self.is_debug:
            self.enable()

    def enable(self):
        self._core.addHandler(self._handler)

    def disable(self):
        self._core.removeHandler(self._handler)

    def set_level(self, level):
        self._core.setLevel(level)
        self._handler.setLevel(level)

    def temp_apply_format(self, fmt_str, level, msg, *args, **kwargs):
        self._handler.setFormatter(GlobalLogFormatter(fmt_str))
        self._core.log(level, msg, *args, **kwargs)
        self._handler.setFormatter(self._fmt)

    @property
    def is_debug(self) -> bool:
        return self._is_debug

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def logger(self):
        return self._core

    @property
    def handler(self):
        return self._handler

    @property
    def formatter(self):
        return self._fmt
