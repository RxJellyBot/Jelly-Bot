import logging

from linebot.models import MemberJoinedEvent, MemberLeftEvent

from external.line.logger import LINE, ExtraKey, event_dest_fmt

__all__ = ["handle_member_main"]


def handle_member_join(event, destination):
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "A user joined the group.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})


def handle_member_left(event, destination):
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "A user left the group.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})


def handle_member_main(event, destination):
    if isinstance(event, MemberJoinedEvent):
        handle_member_join(event, destination)
    elif isinstance(event, MemberLeftEvent):
        handle_member_left(event, destination)
    else:
        LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Unhandled LINE member event.",
                               extra={ExtraKey.Event: event, ExtraKey.Destination: destination})
