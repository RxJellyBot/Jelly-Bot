"""Module for bot feature flags."""
from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum


class BotFeature(FlagDoubleEnum):
    """
    Defined bot feature codes.

        Currently defined bot feature codes are:
        1 - Text
            10 - Main
                100 - Auto Reply
                    1001 - Add

                    1002 - Delete

                    1003 - Add (Execode)

                    1004 - List (Usable)

                    1005 - List (Keyword)

                    1006 - Ranking

                    1009 - Respond

                101 - Timer
                    1011 - Add

                    1012 - List (All)

                    1013 - Delete

                    1019 - List (Keyword)

                102 - Profile
                    1021 - Create

                    1022 - Query

                    1023 - List

                    1024 - Attach

                    1025 - Detach

                    1026 - Delete

            11 - Sub
                110 - Information
                    1101 - Check channel/self ID

                    1102 - Check channel info

                    1103 - Check user info

                    1104 - Check channel member's info

                    1109 - Bot Help

                111 - Transform/Replace
                    1111 - Replace newline character

                112 - Random
                    1121 - Choice - Once

                    1122 - Choice - Multiple

                113 - Recent Activities
                    1131 - Message

                114 - Remote Control
                    1141 - Activate

                    1142 - Deactivate

                    1143 - Current Status

                115 - Calculator
                    1151 - Calculate

                116 - LINE Sticker
                    1161 - Download Animated

                    1162 - Display Static

                    1163 - Download Package

                119 - Other
                    1191 - Ping

            12 - Extra Services
                120 - Short URL
                    1201 - Create

            19 - Functional
                    1901 - User data integration

                    1902 - Calculator

                    1999 - Error Test

        2 - Image
            200 - imgur
                2001 - imgur image upload

        3 - Sticker
            300 - LINE Sticker
                3001 - Get info
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
    TXT_AR_RANKING = \
        1006, _("Text / Auto Reply / Ranking"), \
        _("Get the auto-reply module usage ranking and the unique keyword usage ranking.")
    TXT_AR_INFO = \
        1007, _("Text / Auto Reply / Info"), \
        _("Get the detail of the auto-reply modules which keyword includes the provided keyword.")
    TXT_AR_RESPOND = \
        1009, _("Text / Auto Reply / Respond"), _("Responded to the message origin with the designated response.")

    TXT_TMR_ADD = \
        1011, _("Text / Timer / Add"), _("Add a timer.")
    TXT_TMR_LIST_ALL = \
        1012, _("Text / Timer / List (All)"), _("List all timers.")
    TXT_TMR_DEL = \
        1013, _("Text / Timer / Delete"), _("Delete a timer.")
    TXT_TMR_GET = \
        1019, _("Text / Timer / List (Keyword)"), _("Get the timer(s) with the designated keyword.")

    TXT_PF_CREATE = \
        1021, _("Text / Profile / Create"), _("Add a profile.")
    TXT_PF_QUERY = \
        1022, _("Text / Profile / Query"), _("List profiles which contain the given keyword.")
    TXT_PF_LIST = \
        1023, _("Text / Profile / List"), _("List all profiles.")
    TXT_PF_ATTACH = \
        1024, _("Text / Profile / Attach"), _("Attach a profile to a user.")
    TXT_PF_DETACH = \
        1025, _("Text / Profile / Detach"), _("Detach a profile from a user.")
    TXT_PF_DELETE = \
        1026, _("Text / Profile / Delete"), _("Delete a profile.")

    TXT_INFO_ID = \
        1101, _("Text / Information / Check IDs"), _("Check the ID of current channel and self.")
    TXT_INFO_CHANNEL = \
        1102, _("Text / Information / Channel"), _("Check the channel info.")
    TXT_INFO_USER = \
        1103, _("Text / Information / User"), _("Check the user info of self.")
    TXT_INFO_CHANNEL_MEMBER = \
        1104, _("Text / Information / Channel Member"), _("Check the info of the channel members.")
    TXT_BOT_HELP = \
        1109, _("Text / Information / Help"), _("Get help for how to use the bot and the related information.")

    TXT_TRF_REPL_NEWLINE = \
        1111, _("Text / Transform / Newline"), _("Replace the real newline character to be the escaped character \\n.")

    TXT_RDM_CHOICE_ONE = \
        1121, _("Text / Random / Choice (One)"), _("Randomly pick an option among the provided options.")
    TXT_RDM_CHOICE_MULTI = \
        1122, _("Text / Random / Choice (Multi)"), \
        _("Randomly pick an option among the provided options multiple times.")

    TXT_RCT_MESSAGE = \
        1131, _("Text / Recent / Message"), _("Get recent messages including the recalled ones.")

    TXT_RMC_ACTIVATE = \
        1141, _("Text / Remote / Activate"), _("Activate the remote control system.")
    TXT_RMC_DEACTIVATE = \
        1142, _("Text / Remote / Deactivate"), _("Deactivate the remore control system.")
    TXT_RMC_STATUS = \
        1143, _("Text / Remote / Status"), _("View the current status of the remote control system.")

    TXT_CALCULATOR = \
        1151, _("Text / Calculator"), _("Calculate the given expression string.")

    TXT_LINE_DL_ANIMATED = \
        1161, _("Text / LINE Sticker / Download Animated"), _("Download a specific animated sticker.")
    TXT_LINE_DISP_STATIC = \
        1162, _("Text / LINE Sticker / Display Static"), _("Display a static sticker.")
    TXT_LINE_DL_PACKAGE = \
        1163, _("Text / LINE Sticker / Download Package"), _("Download a sticker package.")

    TXT_PING = \
        1191, _("Text / Ping"), _("Command to check if the bot is working.")

    TXT_SURL_CREATE = \
        1201, _("Text / Short URL / Create"), _("Create a shortened URL.")

    TXT_FN_UDI_START = \
        1901, _("Text / User Data Integration / Start"), _("Issue an Execode for user data integration.")
    TXT_FN_CALCULATOR = \
        1902, _("Text / Calculator"), _("Auto-detected calculator.")
    TXT_FN_ERROR_TEST = \
        1999, _("Text / Error Test"), _("For the purpose of testing the error reporting system.")

    IMG_IMGUR_UPLOAD = \
        2001, _("Image / imgur upload"), _("Upload image to imgur.com.")

    STK_LINE_GET_INFO = \
        3001, _("Sticker / LINE / Get Info"), _("Get the info of the sticker (mostly IDs).")
