# Cookies Keys
class Cookies:
    USER_TOKEN = "utoken"


# Session Keys
class Session:
    USER_ROOT_ID = "x-root-id"

    class APIStatisticsCollection:
        API_ACTION = "x-stats-api-action"
        DICT_PARAMS = "x-stats-param-dict"
        DICT_RESPONSE = "x-stats-resp-dict"
        SUCCESS = "x-stats-success"

        COLLECT = "x-stats-collect"


# Frontend CSS Class
class Css:
    LOGGED_IN_ENABLE = "enable-login"


# Param Dict Prefix
class ParamDictPrefix:
    PostKey = "x-"  # Used in http POST params from HTML forms


# URL Path Parameter Name
class URLPathParameter:
    ChannelOid = "channel_oid"
    ProfileOid = "profile_oid"
