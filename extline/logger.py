"""
This module contains the loggers for the module ``extline``.
"""
import logging

from extutils.logger import LoggerSkeleton

__all__ = ["LINE"]


class LineLoggerSkeleton(LoggerSkeleton):
    """Logger skeleton for LINE bot webhook."""
    KEY_EVENT = "event"
    KEY_DEST = "dest"

    def log_event(self, message, *, level=logging.INFO, event=None, dest=None):
        """Log the LINE event."""
        self.temp_apply_format(
            "%(asctime)s %(name)s[%(levelname)s]: %(message)s\n\tEvent: %(event)s\n\tDestination: %(dest)s",
            level, message, extra={self.KEY_EVENT: event, self.KEY_DEST: dest})


LINE = LineLoggerSkeleton("sys.line", logger_name_env="LINE")
LINE_INTERNAL = LoggerSkeleton("linebot", logger_name_env="LINE_INTERNAL")
