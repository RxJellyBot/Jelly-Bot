import abc
import os
import sys
import logging
import logging.handlers
from pathlib import Path

from django.conf import settings

from extutils import split_fill

__all__ = ["LoggerSkeleton", "SYSTEM"]


LOGGER_SPLITTER = ","
LOGGER_LVSPLIT = "|"


loggers = {}
if "LOGGER" in os.environ:
    for lgr in os.environ["LOGGER"].split(LOGGER_SPLITTER):
        logger_name, lv = split_fill(lgr.strip(), 2, LOGGER_LVSPLIT)
        loggers[logger_name] = int(lv) if lv else lv


class LogFormatter(logging.Formatter):
    default_msec_format = "%s.%03d"


class LogStreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(sys.stdout)


class LogRotatingFileHandlerBase(logging.handlers.RotatingFileHandler, abc.ABC):
    def __init__(self, root, name=None):
        if name:
            path_folder = os.path.join(root, name)
            Path(path_folder).mkdir(parents=True, exist_ok=True)
            path_file = os.path.join(path_folder, "log.log")
        else:
            path_file = root

        super().__init__(path_file, backupCount=10, encoding="utf-8")


class LogFileHandler(LogRotatingFileHandlerBase):
    def __init__(self, name):
        if hasattr(settings, "LOGGING_FILE_ROOT"):
            super().__init__(settings.LOGGING_FILE_ROOT, name)
        else:
            super().__init__("logs", name)


class LogSevereFileHandler(LogRotatingFileHandlerBase):
    def __init__(self):
        if hasattr(settings, "LOGGING_FILE_ERROR"):
            super().__init__(settings.LOGGING_FILE_ERROR)
        else:
            super().__init__("logs-severe.log")

        self.setLevel(logging.WARNING)


class LoggerSkeleton:
    DEFAULT_FMT = "%(asctime)s %(levelname)s [%(name)s] - %(message)s"

    def __init__(self, name: str, fmt: str = None, level: int = None, logger_name_env: str = None):
        # https://docs.python.org/3/library/logging.html#logrecord-attributes

        if logger_name_env is None:
            logger_name_env = name

        if level is None:
            if logger_name_env in loggers:
                level = loggers[logger_name_env]
            elif bool(int(os.environ.get("DEBUG", 0))):
                level = logging.DEBUG
            elif "LOG_LEVEL" in os.environ:
                level = int(os.environ["LOG_LEVEL"])
            else:
                level = logging.WARNING

        # Initialize objects
        self._fmt = LogFormatter(fmt if fmt else LoggerSkeleton.DEFAULT_FMT)
        self._handlers = [
            LogStreamHandler(),
            LogFileHandler(name),
            LogSevereFileHandler()
        ]
        self._handlers_apply_formatter_(self._fmt)
        self._core = logging.getLogger(name)

        # Configs
        self._core.setLevel(level)

        # Activate
        for handler in self._handlers:
            self._core.addHandler(handler)

    def temp_apply_format(self, fmt_str, level, msg, *args, **kwargs):
        self._handlers_apply_formatter_(LogFormatter(fmt_str))
        self._core.log(level, msg, *args, **kwargs)
        self._handlers_apply_formatter_(self._fmt)

    def _handlers_apply_formatter_(self, fmt):
        for handler in self._handlers:
            handler.setFormatter(fmt)

    @property
    def logger(self):
        return self._core

    @property
    def formatter(self):
        return self._fmt


SYSTEM = LoggerSkeleton("sys.main", logger_name_env="SYSTEM", level=logging.DEBUG)
