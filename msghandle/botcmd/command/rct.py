"""
Entry point of the bot command ``JC RCT`` - recent activity.

--------

For recent messages ``JC RCT M``, there are some defaults:

``Bot.RecentActivity.DefaultLimitCountLink``
    Default count of the messages that will be returned as the link to the recent activity page.

``Bot.RecentActivity.DefaultLimitCountDirect``
    Default count of the messages that will be directly output to the command.
"""
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

    # Skip = 1 to skip the message that calls the command
    recent_messages = MessageStatsDataProcessor.get_recent_messages(e.channel_model,
                                                                    limit=limit, tz=e.user_model.config.tzinfo)

    for data in recent_messages.data:
        ctnt.append(f"{data.timestamp} - {data.model.message_content}")

    return HandledMessageEventText(content="\n".join(ctnt))


def _link_recent_msgs(e: TextMessageEventObject, limit: int):
    return HandledMessageEventText(
        content=_("Visit {}{}?{} to see the most recent {} messages. Login required.").format(
            HostUrl,
            reverse(
                "info.channel.recent.message",
                kwargs={"channel_oid": e.channel_oid}
            ),
            QueryDict("", mutable=True).update({"limit": limit}).urlencode(),
            limit
        )
    )


@cmd_msg.command_function(
    feature=BotFeature.TXT_RCT_MESSAGE,
    description=_("This returns recent %d messages.") % Bot.RecentActivity.DefaultLimitCountDirect,
    cooldown_sec=Bot.RecentActivity.CooldownSeconds
)
def get_recent_messages_simple(e: TextMessageEventObject):
    """
    Command to get the most recent messages with default count.

    This command has a cooldown of ``Bot.RecentActivity.CooldownSeconds`` seconds.

    This command will get the most recent ``Bot.RecentActivity.DefaultLimitCountDirect`` messages without the message
    that called this command.

    :param e: message event that calls this command
    :return: default count of most recent messages with a link to the recent activity page
    """
    return get_recent_messages(e, Bot.RecentActivity.DefaultLimitCountLink)


@cmd_msg.command_function(
    feature=BotFeature.TXT_RCT_MESSAGE,
    arg_count=1,
    arg_help=[_("Maximum count of the recent messages to see.")],
    cooldown_sec=Bot.RecentActivity.CooldownSeconds
)
def get_recent_messages(e: TextMessageEventObject, limit: int):
    """
    Command to get the recent message with limited count ``limit``.

    :param e: message event that calls this command
    :param limit: max count of the result to return
    :return: most recent `limit` message with a link to the recent activity page
    """
    return [_content_recent_msgs(e, limit), _link_recent_msgs(e, limit)]
