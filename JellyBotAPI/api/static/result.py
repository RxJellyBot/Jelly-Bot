SUCCESS = "success"
ERRORS = "errors"
FLAGS = "flags"
DATA = "data"
INFO = "info"
RESULT = "result"

REQUIRED = "required"


# TODO: Restruct result keys to reduce the difficulty of building docs (re-categorize)


class Results:
    EXCEPTION = "exception"
    OUTCOME = "outcome"
    MODEL = "model"
    TOKEN = "token"
    HINT = "hint"
    EXPIRY = "expiry"
    ADD_RESULT = "addResult"
    REG_RESULT = "regResult"
    CONN_OUTCOME = "connOutcome"
    INSERT_CONN_OUTCOME = "aConnOutcome"
    LACKING_KEYS = "keysLack"


class AutoReplyResponse:
    KEYWORD = "keyword"
    RESPONSES = "responses"
    CREATOR_OID = "creator"
    PLATFORM = "platform"
    CHANNEL = "channel"
    PRIVATE = "private"
    PINNED = "pinned"
    COOLDOWN_SEC = "cooldown"
