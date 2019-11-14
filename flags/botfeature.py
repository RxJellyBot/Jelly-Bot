from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum


class BotFeature(FlagDoubleEnum):
    """
    1 - Text
        10 - Main
            100 - Auto Reply
                1001 - Add
                1002 - Respond

        11 - Sub
            110 - Information
                1101 - Check channel/self ID
                1102 - Check channel info
                1103 - Check user info
            111 - Transform/Replace
                1111 - Replace newline character

        19 - Functional
                1901 - User data integration
                1902 - Calculator
                1999 - Error Test

    2 - Image
        200 - imgur
            2001 - imgur image upload
    """
    @classmethod
    def default(cls):
        return BotFeature.UNDEFINED

    UNDEFINED = -1, _("Undefined"), _("Undefined bot feature flag.")

    TXT_AR_ADD = \
        1001, _("Text / Auto Reply / Add"), _("Register an auto-reply module.")
    TXT_AR_RESPOND = \
        1002, _("Text / Auto Reply / Respond"), _("Responded to the message origin with the designated response.")

    TXT_INFO_ID = \
        1101, _("Text / Information / Check IDs"), _("Check the ID of current channel and self.")
    TXT_INFO_CHANNEL = \
        1102, _("Text / Information / Channel"), _("Check the channel info.")
    TXT_INFO_USER = \
        1103, _("Text / Information / User"), _("Check the user info of self.")

    TXT_TRF_REPL_NEWLINE = \
        1111, _("Text / Transform / Newline"), _("Replace the real newline character to be the escaped character \\n.")

    TXT_FN_UDI_START = \
        1901, _("Text / User Data Integration / Start"), _("Issue a token for user data integration.")
    TXT_FN_CALCULATOR = \
        1902, _("Text / Calculator"), _("Auto-detected calculator.")
    TXT_FN_ERROR_TEST = \
        1999, _("Text / Error Test"), _("For the purpose of testing the error reporting system.")

    IMG_IMGUR_UPLOAD = \
        2001, _("Image / imgur upload"), _("Upload image to imgur.com.")
