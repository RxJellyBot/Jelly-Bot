import logging

from linebot.models import (
    MessageEvent, FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent,
    MemberJoinedEvent, MemberLeftEvent
)

from external.line.logger import LINE, ExtraKey, event_dest_fmt

from .message import handle_msg_main
from .self import handle_self_main
from .member import handle_member_main
from .error import handle_error


def handle_main(event, destination):
    try:
        if isinstance(event, MessageEvent):
            handle_msg_main(event, destination)
        elif isinstance(event, (FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent)):
            handle_self_main(event, destination)
        elif isinstance(event, (MemberJoinedEvent, MemberLeftEvent)):
            handle_member_main(event, destination)
        else:
            LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Unhandled LINE event.",
                                   extra={ExtraKey.Event: event, ExtraKey.Destination: destination})
    except Exception as e:
        handle_error(e, "Error occurred when handling LINE event.", event, destination)
