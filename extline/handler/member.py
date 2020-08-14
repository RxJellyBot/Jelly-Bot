"""
This module contains various functions to handle various types of member event.
"""
from django.utils.translation import gettext_lazy as _
from linebot.models import MemberJoinedEvent, MemberLeftEvent

from flags import Platform
from mongodb.factory import RootUserManager, ChannelManager, ProfileManager

from ..logger import LINE
from ..wrapper import LineApiUtils, LineApiWrapper

__all__ = ["handle_member_main"]


def handle_member_join(__, event, destination):
    """Method to be called to handle LINE member join event."""
    cdata = ChannelManager.get_channel_token(Platform.LINE, LineApiUtils.get_channel_id(event), auto_register=True)
    joined_names = []

    for user in event.joined.members:
        uid = user.user_id

        udata_result = RootUserManager.get_root_data_onplat(Platform.LINE, uid)

        if udata_result.success and cdata:
            ProfileManager.register_new_default_async(cdata.id, udata_result.model.id)

            uname = RootUserManager.get_root_data_uname(udata_result.model.get_oid(), cdata).user_name
            if uname:
                joined_names.append(uname)

    LINE.log_event("A member joined the group.", event=event, dest=destination)

    LineApiWrapper.reply_text(event.reply_token, _("%s joined the group.") % (" & ".join(joined_names)))


def handle_member_left(__, event, destination):
    """Method to be called to handle LINE member left event."""
    for user in event.left.members:
        uid = user.user_id

        udata_result = RootUserManager.get_root_data_onplat(Platform.LINE, uid)
        cdata = ChannelManager.get_channel_token(Platform.LINE, LineApiUtils.get_channel_id(event), auto_register=True)

        if udata_result.success and cdata:
            ProfileManager.mark_unavailable_async(cdata.id, udata_result.model.id)

    LINE.log_event("A member left the group.", event=event, dest=destination)


def handle_member_main(request, event, destination):
    """Method to be called to handle all types of the member event."""
    if isinstance(event, MemberJoinedEvent):
        handle_member_join(request, event, destination)
    elif isinstance(event, MemberLeftEvent):
        handle_member_left(request, event, destination)
    else:
        LINE.log_event("Unhandled LINE member event.", event=event, dest=destination)
