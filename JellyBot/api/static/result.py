"""Keys to be used for the returned objects via API."""
# pylint: disable=too-few-public-methods

SUCCESS = "success"
ERRORS = "errors"
FLAGS = "flags"
DATA = "data"
INFO = "info"
RESULT = "result"

REQUIRED = "required"


class Common:
    """Common result keys."""

    CREATOR_OID = "creator"
    CHANNEL_OID = "channel"

    TOKEN = "token"
    PLATFORM = "platform"

    MISSING_ARGS = "missingArgs"


class Results:
    """Base result keys (keys that every result object will have)."""

    EXCEPTION = "exception"
    OUTCOME = "outcome"
    MODEL = "model"
    ARGS = "args"
    MISSING_ARGS = Common.MISSING_ARGS


class SenderIdentity:
    """Keys for the identity of the sender."""

    SENDER = "sender"
    PERMISSION = "permission"


class AutoReplyResponse:
    """Keys for the auto-reply module related response."""

    KEYWORD = "keyword"
    RESPONSES = "responses"
    PLATFORM = Common.PLATFORM
    CHANNEL_OID = Common.CHANNEL_OID
    PRIVATE = "private"
    PINNED = "pinned"
    TAGS = "tags"
    COOLDOWN_SEC = "cooldown"


class ExecodeResponse:
    """Keys for the Execode action related response."""

    MISSING_ARGS = Common.MISSING_ARGS
    CREATOR_OID = Common.CREATOR_OID
    COMPLETION_OUTCOME = "cmplOutcome"

    EXECODE = "execode"
    EXPIRY = "expiry"


class UserManagementResponse:
    """Keys for the user management related response."""

    TOKEN = Common.TOKEN
    REG_RESULT = "regResult"
    CONN_OUTCOME = "connOutcome"


class DataQuery:
    """Keys for the user data query related response."""

    COUNT = "count"
    KEYWORD = "keyword"


class Service:
    """Keys for the extra service related response."""

    class ShortUrl:
        """Keys for the short URL related response."""

        SHORTENED_URL = "url"
