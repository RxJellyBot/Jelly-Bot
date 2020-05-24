import logging

from django.utils.translation import gettext_lazy as _

from linebot.models import MemberJoinedEvent, MemberLeftEvent

from flags import Platform
from extline import LINE, ExtraKey, event_dest_fmt, LineApiUtils, LineApiWrapper
from mongodb.factory import RootUserManager, ChannelManager, ProfileManager

__all__ = ["handle_member_main"]


# noinspection PyUnusedLocal
def handle_member_join(request, event, destination):
    cdata = ChannelManager.get_channel_token(Platform.LINE, LineApiUtils.get_channel_id(event), auto_register=True)
    joined_names = []

    for user in event.joined.members:
        uid = user.user_id

        # OPTIMIZE: skip the steps of getting the API / OnPlat model (unnecessary)
        udata_result = RootUserManager.get_root_data_onplat(Platform.LINE, uid)

        if udata_result.success and cdata:
            ProfileManager.register_new_default_async(cdata.id, udata_result.model.id)

            uname = RootUserManager.get_root_data_uname(udata_result.model.get_oid(), cdata).user_name
            if uname:
                joined_names.append(uname)

    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "LINE Join Group.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})

    LineApiWrapper.reply_text(event.reply_token, _("{} joined the group.").format(" & ".join(joined_names)))


# noinspection PyUnusedLocal
def handle_member_left(request, event, destination):
    for user in event.left.members:
        uid = user.user_id

        # OPTIMIZE: skip the steps of getting the API / OnPlat model (unnecessary)
        udata_result = RootUserManager.get_root_data_onplat(Platform.LINE, uid)
        cdata = ChannelManager.get_channel_token(Platform.LINE, LineApiUtils.get_channel_id(event), auto_register=True)

        if udata_result.success and cdata:
            ProfileManager.mark_unavailable_async(cdata.id, udata_result.model.id)

    LINE.temp_apply_format(event_dest_fmt, logging.INFO, "LINE Left Group.",
                           extra={ExtraKey.Event: event, ExtraKey.Destination: destination})


def handle_member_main(request, event, destination):
    if isinstance(event, MemberJoinedEvent):
        handle_member_join(request, event, destination)
    elif isinstance(event, MemberLeftEvent):
        handle_member_left(request, event, destination)
    else:
        LINE.temp_apply_format(event_dest_fmt, logging.INFO, "Unhandled LINE member event.",
                               extra={ExtraKey.Event: event, ExtraKey.Destination: destination})
