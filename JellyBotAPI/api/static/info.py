from django.utils.translation import gettext as _

from extutils.flags import FlagDoubleEnum


class AutoReply(FlagDoubleEnum):
    @staticmethod
    def default():
        return AutoReply.DUMMY

    DUMMY = -1, _("Dummy"), _("Dummy")

    RESPONSES_TRUNCATED = \
        101, _("Response Truncated"), _("The content of response was truncated because its too long.")
    RESPONSE_TYPES_LENGTHENED = \
        102, _("Response Types Lengthened"), \
        _("There are some responses are missing its type so the system filled it with default values.")
    RESPONSE_TYPES_SHORTENED = \
        103, _("Response Types Shortened"), \
        _("We cannot find the corresponding response for some specified response types so the system dropped it.")
