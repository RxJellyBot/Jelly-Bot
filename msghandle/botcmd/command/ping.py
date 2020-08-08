from django.utils.translation import gettext_lazy as _

from flags import BotFeature
from msghandle.models import TextMessageEventObject, HandledMessageEventText

from ._base import CommandNode

cmd = CommandNode(
    codes=["ping"], order_idx=1500, name=_("Ping"),
    description=_("Convenient command to check if the bot is up."))


# noinspection PyUnusedLocal
@cmd.command_function(feature=BotFeature.TXT_PING)
def ping_bot(e: TextMessageEventObject):
    return [HandledMessageEventText(content="OK")]


# noinspection PyUnusedLocal
@cmd.command_function(
    feature=BotFeature.TXT_PING,
    arg_count=1,
    arg_help=[_("Additional text to be attached to the returned message.")]
)
def ping_bot_text_1(e: TextMessageEventObject, txt: str):
    return [HandledMessageEventText(content="OK\nText 1: %s" % txt)]


# noinspection PyUnusedLocal
@cmd.command_function(
    feature=BotFeature.TXT_PING,
    arg_count=2,
    arg_help=[
        _("1st Additional text to be attached to the returned message."),
        _("2nd Additional text to be attached to the returned message.")
    ]
)
def ping_bot_text_2(e: TextMessageEventObject, txt_1: str, txt_2: str):
    return [HandledMessageEventText(content="OK\nText 1: %s\nText 2: %s" % (txt_1, txt_2))]
