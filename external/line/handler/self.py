import logging
from linebot.models import (
    FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent
)

from external.line.logger import LINE, ExtraKey, event_dest_fmt

__all__ = ["handle_self_main"]


def handle_follow(request, event, destination):
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Bot been followed.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})


def handle_unfollow(request, event, destination):
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Bot been unfollowed.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})


def handle_join(request, event, destination):
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Bot joined a group.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})


def handle_leave(request, event, destination):
    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Bot left a group.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})


def handle_self_main(request, event, destination):
    if isinstance(event, FollowEvent):
        handle_follow(request, event, destination)
    elif isinstance(event, UnfollowEvent):
        handle_unfollow(request, event, destination)
    elif isinstance(event, JoinEvent):
        handle_join(request, event, destination)
    elif isinstance(event, LeaveEvent):
        handle_leave(request, event, destination)
    else:
        LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Unahndled bot self event.",
                               extra={ExtraKey.Event: event, ExtraKey.Destination: destination})
