from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum


class AutoReply(FlagDoubleEnum):
    """
    101 - Responses Truncated
    102 - Response Types Lengthened
    103 - Response Types Shortened
    """
    @classmethod
    def default(cls):
        return AutoReply.DUMMY

    DUMMY = -1, _("Dummy"), _("Dummy")

    RESPONSES_TRUNCATED = \
        101, _("Response Truncated"), _("The content of response was truncated because it's too long.")
    RESPONSE_TYPES_LENGTHENED = \
        102, _("Response Types Lengthened"), \
        _("There are some responses are missing its type so the system filled it with default values.")
    RESPONSE_TYPES_SHORTENED = \
        103, _("Response Types Shortened"), \
        _("We cannot find the corresponding response for some specified response types so the system dropped it.")
