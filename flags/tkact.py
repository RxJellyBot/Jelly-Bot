from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum, FlagOutcomeMixin


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

    9xx - System
            901 - Test
    """
    @classmethod
    def default(cls):
        return TokenAction.UNKNOWN

    UNKNOWN = -1, _("Unknown"), _("Unknown Token Action.")

    CONNECT_USER_ON_WEB = \
        101, _("Connect: User Identity"), \
        _("Connect the user identity data between on-platform and API.")
    CONNECT_CHANNEL = \
        111, _("Connect: Register Channel Existence"), \
        _("Confirm the existence in a channel.")
    AR_ADD = \
        201, _("Auto-Reply: Add"), \
        _("Register an Auto-Reply module.")
    SYS_TEST = \
        901, _("System: Test"), \
        _("Preserved for testing purpose.")


class TokenActionCollationFailedReason(FlagDoubleEnum):
    @classmethod
    def default(cls):
        return TokenActionCollationFailedReason.MISC

    MISC = -1, _("Miscellaneous"), _("Miscellaneous collation error occurred.")

    EMPTY_CONTENT = 101, _("Empty Content"), _("The content is empty.")


class TokenActionCompletionOutcome(FlagOutcomeMixin, FlagDoubleEnum):
    """
    # SUCCESS

    < 0 - OK
        -1 - OK

    ================================

    # FAILED

    1xx - Related to Auto Reply
        101 - Error during channel registration
        102 - Error during module registration

    2xx - Related to Identity
        201 - Default profile registratiom
        202 - Channel not found
        203 - Channel error

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

    X_IDT_REGISTER_DEFAULT_PROFILE = \
        201, _("X: Identity - Default Profile Registration"), \
        _("An error occurred during default profile registration.")
    X_IDT_CHANNEL_NOT_FOUND = \
        202, _("X: Identity - Channel not found"), \
        _("Channel data not found using the provided information.")
    X_IDT_CHANNEL_ERROR = \
        203, _("X: Identity - Channel Error"), \
        _("An error occurred during channel data acquiring process.")

    X_MODEL_CONSTRUCTION = \
        501, _("X: Model - Construction"), \
        _("An error occurred during model construction.")

    X_NOT_EXECUTED = \
        901, _("X: Process - Not executed"), \
        _("Token action completion not executed.")
