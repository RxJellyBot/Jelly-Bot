from django.urls import reverse
from django.http import QueryDict
from django.utils.translation import gettext_lazy as _

from flags import BotFeature
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from JellyBot.systemconfig import HostUrl, Bot

from ._base_ import CommandNode

cmd = CommandNode(
    codes=["rct", "recent", "r", "l", "last"], order_idx=500, name=_("Recent Activity"),
    description=_("Check various types of recent activities."))
cmd_msg = cmd.new_child_node(codes=["m", "msg", "message"])


@cmd_msg.command_function(
    feature_flag=BotFeature.TXT_RCT_MESSAGE,
    arg_count=1,
    arg_help=[_("Maximum count of the recent messages to see.")],
    cooldown_sec=Bot.RecentActivity.CooldownSeconds
)
def get_recent_messages(e: TextMessageEventObject, limit: int):
    qd = QueryDict("", mutable=True)
    qd.update({"limit": limit})

    return [HandledMessageEventText(
        content=_("Visit {}{}?{} to see the most recent {} messages.").format(
            HostUrl,
            reverse(
                "info.channel.recent.message",
                kwargs={"channel_oid": e.channel_oid}
            ),
            qd.urlencode(),
            limit)
    )]


@cmd_msg.command_function(
    feature_flag=BotFeature.TXT_RCT_MESSAGE,
    cooldown_sec=Bot.RecentActivity.CooldownSeconds
)
def get_recent_messages_simple(e: TextMessageEventObject):
    return get_recent_messages(e, Bot.RecentActivity.DefaultLimitCount)
