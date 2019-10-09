from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum


class WebsiteError(FlagSingleEnum):
    """
    0 - System
        0 - Unknown
        1 - Extra Content not found

    100 - Identity Data
        100 - Profile link not found
        101 - Channel data not found
        102 - Profile data not found

    200 - Bot
        200 - Command not found
    """

    @classmethod
    def default(cls):
        return WebsiteError.UNKNOWN

    UNKNOWN = 0, _("Unknown")

    EXTRA_CONTENT_NOT_FOUND = 1, _("Extra Content Not Found")

    PROFILE_LINK_NOT_FOUND = 100, _("Profile Link Not Found")
    CHANNEL_NOT_FOUND = 101, _("Profile Link Not Found")
    PROFILE_NOT_FOUND = 102, _("Profile Not Found")

    BOT_CMD_NOT_FOUND = 200, _("Bot Command Not Found")
