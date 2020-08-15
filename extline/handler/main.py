"""This module contains the main function to handle various types of the webhook event."""
from linebot.models import (
    MessageEvent, FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent,
    MemberJoinedEvent, MemberLeftEvent
)

from ..logger import LINE

from .message import handle_msg_main
from .self import handle_self_main
from .member import handle_member_main
from .error import handle_error


def handle_main(request, event, destination):
    """Main handling function to handle various types of event."""
    try:
        if isinstance(event, MessageEvent):
            handle_msg_main(request, event, destination)
        elif isinstance(event, (FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent)):
            handle_self_main(request, event, destination)
        elif isinstance(event, (MemberJoinedEvent, MemberLeftEvent)):
            handle_member_main(request, event, destination)
        else:
            LINE.log_event("Unhandled LINE event.", event=event, dest=destination)
    except Exception as ex:  # pylint: disable=broad-except
        handle_error(ex, "Error occurred when handling LINE event.", event, destination)
