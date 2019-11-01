from django.urls import reverse

from mongodb.helper import MessageStatsDataProcessor
from msghandle.models import TextMessageEventObject
from msghandle.translation import gettext as _
from JellyBot.systemconfig import HostUrl

from ._base_ import CommandNode

cmd = CommandNode(
    ["id", "info"], 500, _("Information"),
    _("Check the information of various things (see the description section for more details)."))
cmd_me = cmd.new_child_node(["me", "my"])
cmd_ch = cmd.new_child_node(["ch", "channel"])


@cmd_me.command_function(description=_("Check the user info of self."))
def check_sender_identity(e: TextMessageEventObject):
    ret = _("User ID: `{}`").format(e.user_model.id)

    if e.user_token:
        ret += "\n" + _("User Token: `{}`").format(e.user_token)

    return ret


@cmd_ch.command_function(description=_("Check the channel info."))
def check_channel_info(e: TextMessageEventObject):
    limit = 10

    mem_stats = list(
        sorted(
            MessageStatsDataProcessor.get_user_messages(
                e.channel_model, hours_within=168).member_stats,
            key=lambda x: x.message_count, reverse=True))[:limit]

    return _("Channel ID: `{}`\n"
             "Channel Token: `{}`\n"
             "\n"
             "Top {} Message Count in 7 Days:\n```\n"
             "{}"
             "\n```\n"
             "Visit {}{} for more details.").format(
        e.channel_oid,
        e.channel_model.token,
        limit,
        "\n".join([f"{entry.message_count:>6} ({entry.message_percentage:>7.02%}) - {entry.user_name}"
                   for entry in mem_stats]),
        HostUrl, reverse("info.channel", kwargs={"channel_oid": e.channel_oid}))
