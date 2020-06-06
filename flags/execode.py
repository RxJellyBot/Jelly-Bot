from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagDoubleEnum, FlagOutcomeMixin


class Execode(FlagDoubleEnum):
    """
    1xx - Identity Management:
        10x - Register Identity:
            101: Channel Membership

        19x - Integrates Identity:
            191: Integrate user data

    2xx - Auto Reply:
            201: Add

    9xx - System
            901 - Test
    """
    @classmethod
    def default(cls):
        return Execode.UNKNOWN

    UNKNOWN = -1, _("Unknown"), _("Unknown Execode.")

    REGISTER_CHANNEL = \
        101, _("Register: Channel Membership"), \
        _("Get the membership of a channel.")
    INTEGRATE_USER_DATA = \
        191, _("Integration: User Data"), \
        _("Integrate user data.")
    AR_ADD = \
        201, _("Auto-Reply: Add"), \
        _("Register an Auto-Reply module.")
    SYS_TEST = \
        901, _("System: Test"), \
        _("Preserved for testing purpose.")


class ExecodeCollationFailedReason(FlagDoubleEnum):
    @classmethod
    def default(cls):
        return ExecodeCollationFailedReason.MISC

    MISC = -1, _("Miscellaneous"), _("Miscellaneous collation error occurred.")

    EMPTY_CONTENT = 101, _("Empty Content"), _("The content is empty.")
    OBJECT_ID_INVALID = 102, _("Invalid OID"), _("ObjectId is invalid.")
    MISSING_KEY = 103, _("Missing Key"), _("Some required keys are missing.")


class ExecodeCompletionOutcome(FlagOutcomeMixin, FlagDoubleEnum):
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
        201 - Default profile registration

        202 - Channel ensure failed

        203 - Channel error

        204 - Integration error

        205 - Integration failed

        206 - Source not found

        207 - Target not found

    5xx - Related to Model
        501 - Error during model construction

    9xx - Related to Process
        901 - Not executed

        902 - Execode not found

        903 - Args lacking
    """
    @classmethod
    def default(cls):
        return ExecodeCompletionOutcome.X_NOT_EXECUTED

    O_OK = \
        -1, _("O: OK"), \
        _("Successfully completed.")

    X_AR_REGISTER_CHANNEL = \
        101, _("X: Auto Reply - Channel Registration"), \
        _("An error occurred during channel registration.")
    X_AR_REGISTER_MODULE = \
        102, _("X: Auto Reply - Module Registration"), \
        _("An error occurred during module registration.")

    X_IDT_REGISTER_DEFAULT_PROFILE = \
        201, _("X: Identity - Default Profile Registration"), \
        _("An error occurred during default profile registration.")
    X_IDT_CHANNEL_ENSURE_FAILED = \
        202, _("X: Identity - Channel ensure failed"), \
        _("Failed to register or ensure the channel data exists.")
    X_IDT_CHANNEL_ERROR = \
        203, _("X: Identity - Channel Error"), \
        _("An error occurred during channel data acquiring process.")
    X_IDT_INTEGRATION_ERROR = \
        204, _("X: Identity - Integration Error"), \
        _("An error occurred during user integration.")
    X_IDT_INTEGRATION_FAILED = \
        205, _("X: Identity - Integration Failed"), \
        _("Failed to integrate the user identity.")
    X_IDT_SOURCE_NOT_FOUND = \
        206, _("X: Identity - Source not found"), \
        _("Source user ID not found in the database.")
    X_IDT_TARGET_NOT_FOUND = \
        207, _("X: Identity - Target not found"), \
        _("Target user ID not found in the database.")
    X_IDT_SOURCE_EQ_TARGET = \
        208, _("X: Identity - Source = Target"), \
        _("Source user ID is equal to target user ID.")

    X_MODEL_CONSTRUCTION = \
        501, _("X: Model - Construction"), \
        _("An error occurred during model construction.")

    X_NOT_EXECUTED = \
        901, _("X: Process - Not executed"), \
        _("Execode completion not executed.")
    X_EXECODE_NOT_FOUND = \
        902, _("X: Process - Execode not found"), \
        _("Execode action not found.")
    X_ARGS_LACKING = \
        903, _("X: Process - Args lacking"), \
        _("Missing required arguments to complete the action.")
