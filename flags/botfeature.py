from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum


class BotFeature(FlagDoubleEnum):
    """
    1 - Text
        10 - Main
            100 - Auto Reply
                1001 - Add
                1002 - Delete
                1003 - Add (Execode)
                1009 - Respond

        11 - Sub
            110 - Information
                1101 - Check channel/self ID
                1102 - Check channel info
                1103 - Check user info
                1109 - Bot Help
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
    TXT_AR_DEL = \
        1002, _("Text / Auto Reply / Delete"), _("Delete an auto-reply module.")
    TXT_AR_ADD_EXECODE = \
        1003, _("Text / Auto Reply / Add (Execode)"), _("Register an auto-reply module using Execode.")
    TXT_AR_LIST_USABLE = \
        1004, _("Text / Auto Reply / List (Usable)"), _("List all the usable auto-reply modules.")
    TXT_AR_LIST_KEYWORD = \
        1005, _("Text / Auto Reply / List (Keyword)"), \
        _("List all the usable auto-reply modules which keyword includes the provided keyword.")
    TXT_AR_RESPOND = \
        1009, _("Text / Auto Reply / Respond"), _("Responded to the message origin with the designated response.")

    TXT_INFO_ID = \
        1101, _("Text / Information / Check IDs"), _("Check the ID of current channel and self.")
    TXT_INFO_CHANNEL = \
        1102, _("Text / Information / Channel"), _("Check the channel info.")
    TXT_INFO_USER = \
        1103, _("Text / Information / User"), _("Check the user info of self.")
    TXT_BOT_HELP = \
        1109, _("Text / Information / Help"), _("Get help for how to use the bot and the related information.")

    TXT_TRF_REPL_NEWLINE = \
        1111, _("Text / Transform / Newline"), _("Replace the real newline character to be the escaped character \\n.")

    TXT_FN_UDI_START = \
        1901, _("Text / User Data Integration / Start"), _("Issue an Execode for user data integration.")
    TXT_FN_CALCULATOR = \
        1902, _("Text / Calculator"), _("Auto-detected calculator.")
    TXT_FN_ERROR_TEST = \
        1999, _("Text / Error Test"), _("For the purpose of testing the error reporting system.")

    IMG_IMGUR_UPLOAD = \
        2001, _("Image / imgur upload"), _("Upload image to imgur.com.")
