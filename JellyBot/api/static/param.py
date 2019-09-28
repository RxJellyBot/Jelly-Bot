LOCAL_REFER = "lr"


class Common:
    CHANNEL_TOKEN = "c"
    CHANNEL_OID = "cid"
    USER_TOKEN = "u"
    USER_OID = "uid"
    PLATFORM = "p"
    API_TOKEN = "api_key"

    COUNT = "count"
    KEYWORD = "w"


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
    TAGS = "tags"


class DataQuery:
    COUNT = Common.COUNT
    KEYWORD = Common.KEYWORD
    USER_OID = Common.USER_OID

    class Channel:
        PLATFORM = Common.PLATFORM
        CHANNEL_TOKEN = Common.CHANNEL_TOKEN
        CHANNEL_OID = Common.CHANNEL_OID


class Manage:
    USER_OID = Common.USER_OID

    class Channel:
        CHANNEL_OID = Common.CHANNEL_OID
        NEW_NAME = "name"


class TokenAction:
    TOKEN = "tk"
    PLATFORM = Common.PLATFORM
    CHANNEL_TOKEN = Common.CHANNEL_TOKEN
    USER_TOKEN = Common.USER_TOKEN
    API_TOKEN = Common.API_TOKEN


class Message:
    MESSAGE = "msg"
    PLATFORM = Common.PLATFORM
    USER_TOKEN = Common.USER_TOKEN
    API_TOKEN = Common.API_TOKEN
