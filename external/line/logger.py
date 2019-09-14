from extutils.logger import LoggerSkeleton

__all__ = ["LINE", "ExtraKey", "event_dest_fmt"]


LINE = LoggerSkeleton("sys.line", logger_name_env="LINE")
LINE_INTERNAL = LoggerSkeleton("linebot", logger_name_env="LINE_INTERNAL")


class ExtraKey:
    Event = "event"
    Destination = "dest"


event_dest_fmt = "%(asctime)s %(name)s[%(levelname)s]: %(message)s\n\tEvent: %(event)s\n\tDestination: %(dest)s"
