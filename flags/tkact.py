from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum


class TokenAction(FlagDoubleEnum):
    """
    1xx - Identity Management:
        10x - Connect User Identity:
            101: Connect Identity (on Web)
            102: Connect Identity (on API)

        11x - Connect Channel Identity:
            111: Register Existence (on Web)
            112: Register Existence (on API)

    2xx - Auto Reply:
            201: Add
    """
    @classmethod
    def default(cls):
        return TokenAction.UNKNOWN

    UNKNOWN = -1, _("Unknown"), _("Unknown Token Action.")

    CONNECT_API_TO_ONPLAT = \
        101, _("Connect: User Identity (on Web)"), \
        _("Connect the API identity to the on-platform identity. (Complete on the website.)")
    CONNECT_ONPLAT_TO_API = \
        102, _("Connect: User Identity (on API)"), \
        _("Connect the on-platform identity to the API identity. (Complete using API side.)")
    CONNECT_CONFIRM_ON_WEB = \
        111, _("Connect: Confirm Channel (on Web)"), \
        _("Confirm the existence in a channel on website.")
    CONNECT_CONFIRM_ON_API = \
        112, _("Connect: Confirm Channel (on API)"), \
        _("Confirm the existence in a channel using API.")
    AR_ADD = \
        201, _("Auto-Reply: Add"), \
        _("Register an Auto-Reply module.")


class TokenActionCollationFailedReason(FlagDoubleEnum):
    @classmethod
    def default(cls):
        return TokenActionCollationFailedReason.MISC

    MISC = -1, _("Miscellaneous"), _("Miscellaneous collation error occurred.")

    EMPTY_CONTENT = 101, _("Empty Content"), _("The content is empty.")


class TokenActionCompletionOutcome(FlagDoubleEnum):
    """
    # SUCCESS

    < 0 - OK
        -1 - OK

    ================================

    # FAILED

    1xx - Related to Auto Reply
        101 - Error during channel registration
        102 - Error during module registration

    5xx - Related to Model
        501 - Error during model construction

    9xx - Related to Process
        901 - Not executed
    """
    @classmethod
    def default(cls):
        return TokenActionCompletionOutcome.X_NOT_EXECUTED

    O_OK = \
        -1, _("O: OK"), \
        _("Successfully completed.")

    X_AR_REGISTER_CHANNEL = \
        101, _("X: Auto Reply - Channel Registration"),\
        _("An error occurred during channel registration.")
    X_AR_REGISTER_MODULE = \
        102, _("X: Auto Reply - Module Registration"), \
        _("An error occurred during module registration.")

    X_MODEL_CONSTRUCTION = \
        501, _("X: Model - Construction"), \
        _("An error occurred during model construction.")

    X_NOT_EXECUTED = \
        901, _("X: Process - Not executed"), \
        _("Token action completion not executed.")

    def is_success(self):
        return self.code < 0
