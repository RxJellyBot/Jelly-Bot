from typing import List

from ttldict import TTLOrderedDict

from JellyBot.systemconfig import System
from msghandle.models import MessageEventObject, HandledMessageEvent, HandledMessageEventText
from strres.msghandle import HandledResult


_sent_cache_ = TTLOrderedDict(System.NoUserTokenNotificationSeconds)


def handle_no_user_token(e: MessageEventObject) -> List[HandledMessageEvent]:
    if e.is_test_event:
        return [HandledMessageEventText(content=HandledResult.TestFailedNoToken)]

    if e.channel_oid not in _sent_cache_:
        _sent_cache_[e.channel_oid] = True

        return [HandledMessageEventText(content=HandledResult.ErrorNoToken, bypass_multiline_check=True)]

    return []
