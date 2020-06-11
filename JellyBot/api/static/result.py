SUCCESS = "success"
ERRORS = "errors"
FLAGS = "flags"
DATA = "data"
INFO = "info"
RESULT = "result"

REQUIRED = "required"


class Common:
    CREATOR_OID = "creator"
    CHANNEL_OID = "channel"

    TOKEN = "token"
    PLATFORM = "platform"

    MISSING_ARGS = "missingArgs"


class Results:
    EXCEPTION = "exception"
    OUTCOME = "outcome"
    MODEL = "model"
    ARGS = "args"
    MISSING_ARGS = Common.MISSING_ARGS


class SenderIdentity:
    SENDER = "sender"
    PERMISSION = "permission"


class AutoReplyResponse:
    KEYWORD = "keyword"
    RESPONSES = "responses"
    PLATFORM = Common.PLATFORM
    CHANNEL_OID = Common.CHANNEL_OID
    PRIVATE = "private"
    PINNED = "pinned"
    TAGS = "tags"
    COOLDOWN_SEC = "cooldown"


class ExecodeResponse:
    MISSING_ARGS = Common.MISSING_ARGS
    CREATOR_OID = Common.CREATOR_OID
    COMPLETION_OUTCOME = "cmplOutcome"

    EXECODE = "execode"
    EXPIRY = "expiry"


class UserManagementResponse:
    TOKEN = Common.TOKEN
    HINT = "hint"
    REG_RESULT = "regResult"
    CONN_OUTCOME = "connOutcome"


class DataQuery:
    COUNT = "count"
    KEYWORD = "keyword"


class Service:
    class ShortUrl:
        SHORTENED_URL = "url"
