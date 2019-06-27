LOCAL_REFER = "lr"


class Common:
    CHANNEL_TOKEN = "c"
    USER_TOKEN = "u"
    PLATFORM = "p"
    API_TOKEN = "api_key"


class Validation:
    CONTENT = "c"
    CONTENT_TYPE = "t"


class AutoReply:
    KEYWORD = "k"
    KEYWORD_TYPE = "kt"
    RESPONSE = "r"
    RESPONSE_TYPE = "rt"
    CHANNEL_TOKEN = Common.CHANNEL_TOKEN
    CREATOR_TOKEN = Common.USER_TOKEN
    API_TOKEN = Common.API_TOKEN
    PLATFORM = Common.PLATFORM
    PRIVATE = "pr"
    PINNED = "pin"
    COOLDOWN = "cd"


class DataQuery:
    class Channel:
        PLATFORM = Common.PLATFORM
        CHANNEL_TOKEN = Common.CHANNEL_TOKEN


class TokenAction:
    TOKEN = "tk"
    PLATFORM = Common.PLATFORM
    USER_TOKEN = Common.USER_TOKEN
