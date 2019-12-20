from typing import List

from django.utils.translation import gettext_lazy as _
from ttldict import TTLOrderedDict

from JellyBot.systemconfig import System, HostUrl
from msghandle.models import MessageEventObject, HandledMessageEvent, HandledMessageEventText


_sent_cache_ = TTLOrderedDict(System.NoUserTokenNotificationSeconds)


def handle_no_user_token(e: MessageEventObject) -> List[HandledMessageEvent]:
    if e.channel_oid not in _sent_cache_:
        _sent_cache_[e.channel_oid] = True

        return [HandledMessageEventText(
            content=_("Bot Features cannot be used as the Bot cannot get your user token.\n"
                      "If you are using LINE, please ensure that you have added Jelly Bot as friend.\n"
                      "Contact the developer via the website ({}) if this issue persists.\n"
                      "\n"
                      "This message will be sent only once in {} seconds per channel when someone without user "
                      "token attempt to use any bot features.").format(
                HostUrl, System.NoUserTokenNotificationSeconds, System.NoUserTokenNotificationSeconds),
            bypass_multiline_check=True
        )]

    return []
