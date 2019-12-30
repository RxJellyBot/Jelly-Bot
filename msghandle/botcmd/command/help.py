from django.utils.translation import gettext_lazy as _

from flags import BotFeature
from msghandle.models import TextMessageEventObject, HandledMessageEventText

from ._base_ import CommandNode

cmd = CommandNode(
    codes=["help"], order_idx=1000, name=_("Help"),
    description=_("See the documentation or bot related information."))


# noinspection PyUnusedLocal
@cmd.command_function(feature_flag=BotFeature.TXT_BOT_HELP)
def help_text(e: TextMessageEventObject):
    # For some reason, translation needs to be casted to `str` explicitly, or:
    #   - LINE cannot respond anything
    #   - Discord will not change the language
    return [
        HandledMessageEventText(
            content=str(_("LINE: http://rnnx.cc/Line\n"
                          "Discord: http://rnnx.cc/Discord\n"
                          "Website: http://rnnx.cc/Website")),
            bypass_multiline_check=True
        )
    ]
