LOCAL_REFER = "lr"


class _Common:
    CHANNEL_TOKEN = "c"
    USER_TOKEN = "u"
    PLATFORM = "p"


class Validation:
    CONTENT = "c"
    CONTENT_TYPE = "t"


class AutoReply:
    KEYWORD = "k"
    KEYWORD_TYPE = "kt"
    RESPONSE = "r"
    RESPONSE_TYPE = "rt"
    CHANNEL_TOKEN = _Common.CHANNEL_TOKEN
    CREATOR_TOKEN = _Common.USER_TOKEN
    PLATFORM = _Common.PLATFORM
    PRIVATE = "pr"
    PINNED = "pin"
    COOLDOWN = "cd"


class DataQuery:
    class Channel:
        PLATFORM = _Common.PLATFORM
        CHANNEL_TOKEN = _Common.CHANNEL_TOKEN


class TokenAction:
    TOKEN = "tk"
    PLATFORM = _Common.PLATFORM
    USER_TOKEN = _Common.USER_TOKEN
