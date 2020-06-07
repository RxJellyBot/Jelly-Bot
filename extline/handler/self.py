"""
This module contains various functions to handle event related to the LINE bot.
"""
from linebot.models import (
    FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent
)

from flags import Platform
from mongodb.factory import ChannelManager

from ..logger import LINE
from ..wrapper import LineApiUtils

__all__ = ["handle_self_main"]


def handle_follow(_, event, destination):
    """Method to be called when the bot being followed/added as a friend."""
    LINE.log_event("Bot followed.", event=event, dest=destination)


def handle_unfollow(_, event, destination):
    """Method to be called when the bot being unfollowed/blocked."""
    LINE.log_event("Bot unfollowed.", event=event, dest=destination)


def handle_join(_, event, destination):
    """Method to be called when the bot joined a group."""
    LINE.log_event("Bot joined a group.", event=event, dest=destination)
    ChannelManager.ensure_register(Platform.LINE, LineApiUtils.get_channel_id(event))


def handle_leave(_, event, destination):
    """Method to be called when the bot left a group."""
    LINE.log_event("Bot left a group.", event=event, dest=destination)
    ChannelManager.deregister(Platform.LINE, LineApiUtils.get_channel_id(event))


def handle_self_main(request, event, destination):
    """Method to be called to handle all types of the event related to the bot."""
    if isinstance(event, FollowEvent):
        handle_follow(request, event, destination)
    elif isinstance(event, UnfollowEvent):
        handle_unfollow(request, event, destination)
    elif isinstance(event, JoinEvent):
        handle_join(request, event, destination)
    elif isinstance(event, LeaveEvent):
        handle_leave(request, event, destination)
    else:
        LINE.log_event("Unahndled bot self event.", event=event, dest=destination)
