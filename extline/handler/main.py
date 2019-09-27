import logging

from linebot.models import (
    MessageEvent, FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent,
    MemberJoinedEvent, MemberLeftEvent
)

from ..logger import LINE, ExtraKey, event_dest_fmt
from .message import handle_msg_main
from .self import handle_self_main
from .member import handle_member_main
from .error import handle_error


def handle_main(request, event, destination):
    try:
        if isinstance(event, MessageEvent):
            handle_msg_main(request, event, destination)
        elif isinstance(event, (FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent)):
            handle_self_main(request, event, destination)
        elif isinstance(event, (MemberJoinedEvent, MemberLeftEvent)):
            handle_member_main(request, event, destination)
        else:
            LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Unhandled LINE event.",
                                   extra={ExtraKey.Event: event, ExtraKey.Destination: destination})
    except Exception as e:
        handle_error(e, "Error occurred when handling LINE event.", event, destination)
