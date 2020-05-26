from typing import List

from django.utils.translation import gettext_lazy as _

from flags import BotFeature, CommandScopeCollection
from msghandle.models import TextMessageEventObject, HandledMessageEventText
from mongodb.factory import ShortUrlDataManager

from ._base import CommandNode

cmd = CommandNode(
    codes=["surl", "short", "st", "url"], order_idx=800, name=_("Shorten URL"),
    description=_("Commands related to the Short URL service."))


# noinspection PyUnusedLocal
@cmd.command_function(
    arg_count=1, arg_help=[_("URL to be shortened.")],
    feature_flag=BotFeature.TXT_SURL_CREATE,
    scope=CommandScopeCollection.PRIVATE_ONLY)
def replace_newline(e: TextMessageEventObject, original_url: str) -> List[HandledMessageEventText]:
    result = ShortUrlDataManager.create_record(original_url, e.user_model.id)
    if result.success:
        return [HandledMessageEventText(content=_("URL Shortened.")),
                HandledMessageEventText(content=result.model.short_url)]
    else:
        return [
            HandledMessageEventText(content=_("Failed to shorten the URL. Code: {}").format(result.outcome.code_str))
        ]
