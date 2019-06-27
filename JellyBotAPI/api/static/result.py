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

    LACKING_KEYS = "keysLack"


class Results:
    EXCEPTION = "exception"
    OUTCOME = "outcome"
    MODEL = "model"
    LACKING_KEYS = Common.LACKING_KEYS


class SenderIdentity:
    SENDER = "sender"


class AutoReplyResponse:
    KEYWORD = "keyword"
    RESPONSES = "responses"
    PLATFORM = Common.PLATFORM
    CHANNEL_OID = Common.CHANNEL_OID
    PRIVATE = "private"
    PINNED = "pinned"
    COOLDOWN_SEC = "cooldown"

    ADD_RESULT = "addResult"


class TokenActionResponse:
    LACKING_KEYS = Common.LACKING_KEYS
    CREATOR_OID = Common.CREATOR_OID
    COMPLETION_RESULT = "cmplResult"

    TOKEN = Common.TOKEN
    EXPIRY = "expiry"


class UserManagementResponse:
    TOKEN = Common.TOKEN
    HINT = "hint"
    REG_RESULT = "regResult"
    CONN_OUTCOME = "connOutcome"


class ChannelDataQueryResponse:
    PLATFORM = Common.PLATFORM
    CHANNEL_OID = Common.CHANNEL_OID
