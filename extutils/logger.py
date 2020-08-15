"""Module of the customized logger implementations."""
import abc
import os
import sys
import logging
import logging.handlers
from pathlib import Path

from django.conf import settings

__all__ = ("LoggerSkeleton", "SYSTEM", "ENV_VAR_NAME_LOGGER", "ENV_VAR_NAME_LOG_LEVEL",)

LOGGER_SPLITTER = ","
LOGGER_LVSPLIT = "|"

ENV_VAR_NAME_LOGGER = "LOGGER"
ENV_VAR_NAME_LOG_LEVEL = "LOG_LEVEL"

LOGGERS = {}
if ENV_VAR_NAME_LOGGER in os.environ:
    from .utils import split_fill

    for lgr in os.environ[ENV_VAR_NAME_LOGGER].split(LOGGER_SPLITTER):
        logger_name, lv = split_fill(lgr.strip(), 2, delim=LOGGER_LVSPLIT)
        LOGGERS[logger_name] = int(lv) if lv else lv


class LogFormatter(logging.Formatter):
    """
    Formatter for each log entries.

    ``default_msec_format`` is the format for timestamp seconds of the entry.
    """

    default_msec_format = "%s.%03d"


class LogStreamHandler(logging.StreamHandler):
    """Log output stream handler. Default to ``sys.stdout``."""

    def __init__(self):
        super().__init__(sys.stdout)


def get_log_file_path(root, name_logger=None):
    """
    Get the path for the log file.

    Returns ``{root}/{name_logger}/log.log`` if ``name_logger`` is specified.

    Otherwise, returns ``root``.

    :param root: root directory/path for the log
    :param name_logger: name of the logger
    :return: path of the log file
    """
    if not name_logger:
        return root

    path_folder = os.path.join(root, name_logger)
    Path(path_folder).mkdir(parents=True, exist_ok=True)
    return os.path.join(path_folder, "log.log")


class LogTimedRotatingFileHandlerBase(logging.handlers.TimedRotatingFileHandler, abc.ABC):
    """Base class for the timed rotating file handler."""

    def __init__(self, root, name=None):
        super().__init__(get_log_file_path(root, name), when="midnight", backupCount=10, encoding="utf-8")


class LogRotatingFileHandlerBase(logging.handlers.RotatingFileHandler, abc.ABC):
    """Base class for the rotating file handler."""

    def __init__(self, root, name=None):
        super().__init__(get_log_file_path(root, name), backupCount=10, encoding="utf-8")


class LogFileHandler(LogTimedRotatingFileHandlerBase):
    """Log file handler."""

    def __init__(self, name):
        if hasattr(settings, "LOGGING_FILE_ROOT"):
            super().__init__(settings.LOGGING_FILE_ROOT, name)
        else:
            super().__init__("logs", name)


class LogSevereFileHandler(LogRotatingFileHandlerBase):
    """Severe log file handler."""

    def __init__(self):
        if hasattr(settings, "LOGGING_FILE_ERROR"):
            super().__init__(settings.LOGGING_FILE_ERROR)
        else:
            super().__init__("logs-severe.log")

        self.setLevel(logging.WARNING)


class LoggerSkeleton:
    """
    A logger skeleton class to manage a logger.

    The logger's level is determined in the following order:
        > Level specified in env var ``LOGGER``
            - see `note.md`
        > ``DEBUG`` env var
            - ``logging.DEBUG`` if set to 1
        > Log level specified in env var ``LOG_LEVEL``
            - see `note.md`

    If none of the above matches. then the default level will be set to ``logging.WARNING``.
    """

    DEFAULT_FMT = "%(asctime)s %(levelname)s [%(name)s] - %(message)s"

    def __init__(self, name: str, fmt: str = None, level: int = None, logger_name_env: str = None):
        # https://docs.python.org/3/library/logging.html#logrecord-attributes

        if logger_name_env is None:
            logger_name_env = name

        if level is None:
            if logger_name_env in LOGGERS:
                level = LOGGERS[logger_name_env]
            elif settings.DEBUG:
                level = logging.DEBUG
            elif ENV_VAR_NAME_LOG_LEVEL in os.environ:
                level = int(os.environ[ENV_VAR_NAME_LOG_LEVEL])
            else:
                level = logging.WARNING

        # Initialize objects
        self._fmt = LogFormatter(fmt if fmt else LoggerSkeleton.DEFAULT_FMT)
        self._handlers = [
            LogStreamHandler(),
            LogFileHandler(name),
            LogSevereFileHandler()
        ]
        self._handlers_apply_formatter(self._fmt)
        self._core = logging.getLogger(name)

        # Configs
        self._core.setLevel(level)

        # Activate
        for handler in self._handlers:
            self._core.addHandler(handler)

    def temp_apply_format(self, fmt_str, level, msg, *args, **kwargs):
        """
        Temporarily apply the log format for this log entry.

        :param fmt_str: formatting string
        :param level: level of the log
        :param msg: log message
        :param args: args for `log()`
        :param kwargs: kwargs for `log()`
        """
        self._handlers_apply_formatter(LogFormatter(fmt_str))
        self._core.log(level, msg, *args, **kwargs)
        self._handlers_apply_formatter(self._fmt)

    def _handlers_apply_formatter(self, fmt):
        for handler in self._handlers:
            handler.setFormatter(fmt)

    @property
    def logger(self):
        """
        Get the core logger.

        :return: core logger
        """
        return self._core

    @property
    def formatter(self):
        """
        Get the log formatter.

        :return: log formatter
        """
        return self._fmt


SYSTEM = LoggerSkeleton("sys.main", logger_name_env="SYSTEM", level=logging.DEBUG)
