from django.urls import reverse
from django.http import QueryDict
from django.utils.translation import gettext_lazy as _

from flags import BotFeature
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from mongodb.helper import MessageStatsDataProcessor
from JellyBot.systemconfig import HostUrl, Bot

from ._base import CommandNode

cmd = CommandNode(
    codes=["rct", "recent", "r", "l", "last"], order_idx=500, name=_("Recent Activity"),
    description=_("Check various types of recent activities."))
cmd_msg = cmd.new_child_node(codes=["m", "msg", "message"])


def _content_recent_msgs(e: TextMessageEventObject, limit: int):
    limit = min(Bot.RecentActivity.DefaultLimitCountDirect, limit)

    ctnt = []

    recent_messages = MessageStatsDataProcessor.get_recent_messages(e.channel_model, limit, e.user_model.config.tzinfo)

    for data in recent_messages.data:
        ctnt.append(f"{data.timestamp} - {data.model.message_content}")

    return HandledMessageEventText(content="\n".join(ctnt))


def _link_recent_msgs(e: TextMessageEventObject, limit: int):
    qd = QueryDict("", mutable=True)
    qd.update({"limit": limit})

    return HandledMessageEventText(
        content=_("Visit {}{}?{} to see the most recent {} messages. Login required.").format(
            HostUrl,
            reverse(
                "info.channel.recent.message",
                kwargs={"channel_oid": e.channel_oid}
            ),
            qd.urlencode(),
            limit)
    )


@cmd_msg.command_function(
    feature_flag=BotFeature.TXT_RCT_MESSAGE,
    arg_count=1,
    arg_help=[_("Maximum count of the recent messages to see.")],
    cooldown_sec=Bot.RecentActivity.CooldownSeconds
)
def get_recent_messages(e: TextMessageEventObject, limit: int):
    return [_content_recent_msgs(e, limit), _link_recent_msgs(e, limit)]


@cmd_msg.command_function(
    feature_flag=BotFeature.TXT_RCT_MESSAGE,
    cooldown_sec=Bot.RecentActivity.CooldownSeconds
)
def get_recent_messages_simple(e: TextMessageEventObject):
    return get_recent_messages(e, Bot.RecentActivity.DefaultLimitCountLink)
