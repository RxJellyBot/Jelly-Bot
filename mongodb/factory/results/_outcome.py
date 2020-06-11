from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagPrefixedDoubleEnum, FlagOutcomeMixin


class BaseOutcome(FlagOutcomeMixin, FlagPrefixedDoubleEnum):
    @property
    def code_prefix(self) -> str:
        raise NotImplementedError()

    @property
    def code_str(self) -> str:
        return f"{self.code_prefix}-{self._code}"

    @classmethod
    def default(cls):
        raise NotImplementedError()


class WriteOutcome(BaseOutcome):
    """
    # SUCCESS

    -2xx - Actually Inserted
        -201 - Inserted

    -1xx - Not actually inserted
        -101 - Existed
        -151 - Updated

    -x - Miscellaneous
        -1 - Uncategorized

    ================================

    # FAILED

    1xx - Problems related to the preparation processes
        101 - Insufficient Permission

        102 - Channel type identification failed

        103 - (Auto Reply) Pinned module existed

        104 - Channel registration failed

        105 - OnPlatform user registration failed

        106 - API user registration failed

        107 - OnPlatform user identity connection failed

        108 - API user identity connection failed

        109 - Config setting failed

        110 - Invalid URL

        111 - (Auto Reply) Invalid keyword content

        112 - (Auto Reply) Invalid response content

        113 - (Channel) Default profile creation failed

        114 - Empty content

        115 - (Execode) Unknown action

    2xx - Problems related to the model
        201 - Not serializable

        202 - Not acknowledged

        204 - Not entry

        205 - Invalid

        206 - Field key not exists

    3xx - Problems related to the field of an model
        301 - Field readonly

        302 - Field type mismatch

        303 - Field invalid

        304 - Field casting failed

        305 - Required key not filled

        399 - Misc

    4xx - Problems related to cache
        401 - Missing in cache, attempted insertion

        402 - Missing in cache, aborted insertion

    5ss - Problems related to intermediate process
        501 - Channel not found

        502 - Model class not provided

    8xx - Unknown Problems
        801 - Model construction unknown

        802 - Insertion unknown

    9xx - Problems related to execution
        901 - Not executed

        902 - Exception occurred
    """
    @property
    def code_prefix(self) -> str:
        return "I"

    @classmethod
    def default(cls):
        return WriteOutcome.X_NOT_EXECUTED

    O_INSERTED = \
        -201, _("O: Inserted"), _("Data inserted.")
    O_UPDATED = \
        -151, _("O: Updated"), _("Data updated.")
    O_DATA_EXISTS = \
        -101, _("O: Existed"), _("Data already exists.")
    O_MISC = \
        -1, _("O: Uncategorized"), _("Uncategorized success reason.")
    X_INSUFFICIENT_PERMISSION = \
        101, _("X: Insufficient permission"), \
        _("Insufficient permission to perform the action.")
    X_CHANNEL_TYPE_UNKNOWN = \
        102, _("X: Channel type unidentifiable"), \
        _("The channel type is unidentifiable using the provided token and platform.")
    X_PINNED_CONTENT_EXISTED = \
        103, _("X: Pinned module existed"), \
        _("A pinned auto-reply module has already existed.")
    X_ON_REG_CHANNEL = \
        104, _("X: Channel registration failed"), \
        _("Channel registration failed.")
    X_ON_REG_ONPLAT = \
        105, _("X: OnPlatform user registration failed"), \
        _("OnPlatform user registration failed.")
    X_ON_REG_API = \
        106, _("X: API user registration failed"), \
        _("API user registration failed.")
    X_ON_CONN_ONPLAT = \
        107, _("X: OnPlatform user connection failed"), \
        _("OnPlatform user identity connection failed.")
    X_ON_CONN_API = \
        108, _("X: API user connection failed"), \
        _("API user identity connection failed.")
    X_ON_SET_CONFIG = \
        109, _("X: Failed to set config"), \
        _("Failed to set the config value.")
    X_INVALID_URL = \
        110, _("X: Invalid URL"), \
        _("The URL is invalid.")
    X_AR_INVALID_KEYWORD = \
        111, _("X: Invalid Keyword"), \
        _("The keyword contains invalid content.")
    X_AR_INVALID_RESPONSE = \
        112, _("X: Invalid Response"), \
        _("One or more of the responses contains invalid content.")
    X_CNL_DEFAULT_CREATE_FAILED = \
        113, _("X: Default profile creation failed"), \
        _("Failed to create a default profile for the channel.")
    X_EMPTY_CONTENT = \
        114, _("X: Empty content"), \
        _("The content to be stored is empty.")
    X_UNKNOWN_EXECODE_ACTION = \
        115, _("X: Unknown Execode action"), \
        _("The action type of the Execode is unknown.")
    X_NOT_SERIALIZABLE = \
        201, _("X: Not serializable"), \
        _("The data to be stored cannot be serialized.")
    X_NOT_ACKNOWLEDGED = \
        202, _("X: Not acknowledged"), \
        _("The database did not acknowledge the data to be inserted.")
    X_NOT_MODEL = \
        204, _("X: Not model"), \
        _("The data is not a model.")
    X_INVALID_MODEL = \
        205, _("X: Invalid model"), \
        _("Some data of the model is invalid.")
    X_MODEL_KEY_NOT_EXIST = \
        206, _("X: Model not exist"), \
        _("Some model key does not exist.")
    X_READONLY = \
        301, _("X: Readonly"), \
        _("Some fields to be written is readonly.")
    X_TYPE_MISMATCH = \
        302, _("X: Type mismatch"), \
        _("Some data type of the value is not the expected one.")
    X_INVALID_FIELD_VALUE = \
        303, _("X: Invalid field value"), \
        _("Some model field value is invalid.")
    X_CASTING_FAILED = \
        304, _("X: Casting failed"), \
        _("Some data cannot be casted to the desired type.")
    X_REQUIRED_NOT_FILLED = \
        305, _("X: Required not filled"), \
        _("Required value(s) of the model not filled.")
    X_INVALID_MODEL_FIELD = \
        399, _("X: Invalid model field"), \
        _("There are fields in the model containing invalid values.")
    X_NOT_FOUND_ATTEMPTED_INSERT = \
        401, _("X: Not found - attempted insert"), \
        _("Data not found. Attempted to insert but failed.")
    X_NOT_FOUND_ABORTED_INSERT = \
        402, _("X: Not found - aborted insert"), \
        _("Data not found. Insertion was not attempted.")
    X_CHANNEL_NOT_FOUND = \
        501, _("X: Channel not found"), \
        _("Channel not found.")
    X_NO_MODEL_CLASS = \
        502, _("X: No model class"), \
        _("Model class not provided.")
    X_CONSTRUCT_UNKNOWN = \
        801, _("X: Model construction"), \
        _("An unknown occurred during the construction of a data model.")
    X_INSERT_UNKNOWN = \
        802, _("X: Insertion"), \
        _("An unknown occurred during the insertion of the data.")
    X_NOT_EXECUTED = \
        901, _("X: Not executed"), \
        _("Insertion not executed.")
    X_EXCEPTION_OCCURRED = \
        902, _("X: Exception occurred"), \
        _("An exception occurred.")

    @property
    def is_inserted(self):
        return self.code < -200

    @property
    def data_found(self):
        return -199 < self.code < -100


class GetOutcome(BaseOutcome):
    """
    # SUCCESS

    -2 - Already exists

    -1 - Inserted

    ================================

    # FAILED

    1xx - Problems related to the getting process
        101 - Not Found, attempted insert

        102 - Not Found, aborted insert

    2xx - Problems related to the given parameters
        201 - The content is empty

    3xx - SPECIFIC
        30x - Permission
            301 - Channel not found

            302 - Error during config creation

            303 - Error during default profile creation

        31x - Execode
            311 - Incorrect Execode type

    9xx - Problems related to execution
        901 - Not executed
    """
    @property
    def code_prefix(self) -> str:
        return "G"

    @classmethod
    def default(cls):
        return GetOutcome.X_NOT_EXECUTED

    O_CACHE_DB = \
        -2, _("O: Data found"), \
        _("The data was found.")
    O_ADDED = \
        -1, _("O: Inserted"), \
        _("The data was not found but inserted.")

    X_NOT_FOUND_ATTEMPTED_INSERT = \
        101, _("X: Not found - attempted insert"), \
        _("Data not found. Attempted to insert but failed.")
    X_NOT_FOUND_ABORTED_INSERT = \
        102, _("X: Not found - aborted insert"), \
        _("Date not found. Insertion was not attempted.")
    X_NOT_FOUND_FIRST_QUERY = \
        103, _("X: Not found on 1st query"), \
        _("Data not found at the 1st query.")
    X_NOT_FOUND_SECOND_QUERY = \
        104, _("X: Not found on 2nd query"), \
        _("Data not found at the 2nd query.")
    X_NO_CONTENT = \
        201, _("X: Empty Content"), \
        _("The content is empty.")
    X_CHANNEL_NOT_FOUND = \
        301, _("X: Channel not found"), \
        _("Channel not found.")
    X_CHANNEL_CONFIG_ERROR = \
        302, _("X: Config error"), \
        _("An error occurred during the access of channel config.")
    X_DEFAULT_PROFILE_ERROR = \
        303, _("X: Default profile error"), \
        _("An error occurred during the creation of the default profile.")
    X_EXECODE_TYPE_MISMATCH = \
        311, _("X: Execode type mismatch"), \
        _("The type of the given Execode does not match the desired one.")
    X_NOT_EXECUTED = \
        901, _("X: Not executed"), \
        _("Process not executed.")


class OperationOutcome(BaseOutcome):
    """
    # SUCCESS

    -1xx - Success with some potential problems
        -101 - Additional args omitted

        -102 - Readonly args omitted

    -1 - Operation completed

    ================================

    # FAILED

    1xx - Problems related to Execode
        101 - Execode not found

        102 - Required arguments missing

        103 - Completion failed

        104 - Completion process not implemented

        105 - Completion error

        106 - Empty Execode

        107 - Collation error

        108 - Type mismatch

    2xx - Problems related to channel
        201 - Channel not found

    3xx - Problems related to user data
        301 - Source is identical to destination

        302 - Source user data not found

        303 - Destination user data not found

    4xx - Problems related to profile control
        401 - Insufficient permission

        402 - Cannot be attached

        403 - Profile not found with the name

        404 - No attachable profiles

        405 - Target not in channel

        406 - Detach failed

        407 - Invalid permission level

        408 - Invalid color

        409 - Empty args

    5xx - Problems related to model
        501 - Construction error

    9xx - Problems related to execution
        901 - Not executed

        902 - Not updated

        903 - not deleted

        904 - User integration failed

        999 - Error
    """

    @property
    def code_prefix(self) -> str:
        return "O"

    @classmethod
    def default(cls):
        return OperationOutcome.X_NOT_EXECUTED

    O_ADDL_ARGS_OMITTED = \
        -101, _("O: Additional args omitted"), \
        _("Operation succeed. Some additional arguments were omitted.")
    O_READONLY_ARGS_OMITTED = \
        -102, _("O: Readonly args omitted"), \
        _("Operation succeed. Some arguments are omitted because it is readonly.")
    O_COMPLETED = \
        -1, _("O: Completed"), \
        _("The operation was successfully completed.")
    X_EXECODE_NOT_FOUND = \
        101, _("X: Execode not found"), \
        _("No enqueued Execode found.")
    X_MISSING_ARGS = \
        102, _("X: Required arguments missing"), \
        _("Missing required arguments to complete the action.")
    X_COMPLETION_FAILED = \
        103, _("X: Completion failed"), \
        _("The action completion was failed.")
    X_NO_COMPLETE_ACTION = \
        104, _("X: No complete action"), \
        _("Complete action not implemented for the provided action type.")
    X_COMPLETION_ERROR = \
        105, _("X: Completion error"), \
        _("An error occurred during the action completion process.")
    X_EXECODE_EMPTY = \
        106, _("X: Empty Execode"), \
        _("The Execode is empty.")
    X_COLLATION_ERROR = \
        107, _("X: Collation error"), \
        _("An error occurred during the parameter collating process.")
    X_EXECODE_TYPE_MISMATCH = \
        108, _("X: Execode type mismatch"), \
        _("The type of the Execode does not match the desired one.")
    X_CHANNEL_NOT_FOUND = \
        201, _("X: Channel not found"), \
        _("Channel not found.")
    X_SAME_SRC_DEST = \
        301, _("X: Source = Destination"), \
        _("Source user data is identical to the destination user data.")
    X_SRC_DATA_NOT_FOUND = \
        302, _("X: Source data not found"), \
        _("Source user data not found.")
    X_DEST_DATA_NOT_FOUND = \
        303, _("X: Destination data not found"), \
        _("Destination user data not found.")
    X_INSUFFICIENT_PERMISSION = \
        401, _("X: Insufficient permission"), \
        _("Insufficient permission to execute this operation.")
    X_UNATTACHABLE = \
        402, _("X: Unattachable"), \
        _("The profile cannot be attached to the target.")
    X_PROFILE_NOT_FOUND_NAME = \
        403, _("X: Profile not found (name)"), \
        _("Profile not found with the given name.")
    X_NO_ATTACHABLE_PROFILES = \
        404, _("X: No attachable profiles"), \
        _("No attachable profiles.")
    X_TARGET_NOT_IN_CHANNEL = \
        405, _("X: Target not in channel"), \
        _("The target to be attached the profile is not in the channel.")
    X_DETACH_FAILED = \
        406, _("X: Detach failed"), \
        _("Failed to detach the profile from the target.")
    X_INVALID_PERM_LV = \
        407, _("X: Invalid permission level"), \
        _("The value of the permission level is invalid.")
    X_INVALID_COLOR = \
        408, _("X: Invalid color"), \
        _("The value of the color is invalid.")
    X_EMPTY_ARGS = \
        409, _("X: Empty arguments"), \
        _("The parsed arguments is empty.")
    X_CONSTRUCTION_ERROR = \
        501, _("X: Construction error"), \
        _("An error occurred during model construction.")
    X_NOT_EXECUTED = \
        901, _("X: Not executed"), \
        _("The operation had not been executed.")
    X_NOT_UPDATED = \
        902, _("X: Not updated"), \
        _("Update operation not performed.")
    X_NOT_DELETED = \
        903, _("X: Not deleted"), \
        _("Delete operation not performed.")
    X_INTEGRATION_FAILED = \
        904, _("X: User integration failed"), \
        _("ID replacement process of user integration failed.")
    X_ERROR = \
        999, _("X: Error"), \
        _("An error occurred during the execution.")


class UpdateOutcome(BaseOutcome):
    """
    # SUCCESS

    -1xx - Potentially problematic update

        -101 - Found (not updated)

        -102 - Partial args removed

        -103 - Value invalid

    -1 - Updated

    ================================

    # FAILED

    1xx - Problems related to model
        101 - Model not found

        102 - Args parsing failed

    2xx - Problems related to model field
        N/A

    3xx - Problems related to the intermediate process
        301 - Channel not found

        302 - Config not exists

        303 - Config type mismatch

        304 - Config value invalid

        305 - Insufficient permission

    9xx - Problems related to execution
        901 - Not executed
    """

    @property
    def code_prefix(self) -> str:
        return "U"

    @classmethod
    def default(cls):
        return UpdateOutcome.X_NOT_EXECUTED

    O_FOUND = \
        -101, _("O: Found"), \
        _("The data was found but not updated.")
    O_PARTIAL_ARGS_REMOVED = \
        -102, _("O: Partial args removed"), \
        _("Some arguments are removed.")
    O_PARTIAL_ARGS_INVALID = \
        -103, _("O: Partial args invalid"), \
        _("Some arguments are invalid.")

    O_UPDATED = \
        -1, _("O: Success"), \
        _("Successfully updated")

    X_NOT_FOUND = \
        101, _("X: Not found"), \
        _("No data to be updated.")
    X_ARGS_PARSE_FAILED = \
        102, _("X: Args parsing failed"), \
        _("Failed to parse the arguments.")

    X_CHANNEL_NOT_FOUND = \
        301, _("X: Channel not found"), \
        _("Channel not found.")
    X_CONFIG_NOT_EXISTS = \
        302, _("X: Config not exists"), \
        _("Specified config field does not exist.")
    X_CONFIG_TYPE_MISMATCH = \
        303, _("X: Config type mismatch"), \
        _("The type of the new value does not match the expected type(s) of the config.")
    X_CONFIG_VALUE_INVALID = \
        304, _("X: Config value invalid"), \
        _("The new config value is invalid for the corresponding field.")
    X_INSUFFICIENT_PERMISSION = \
        305, _("X: Insufficient permission"), \
        _("Insufficient permission to complete the action.")

    X_NOT_EXECUTED = \
        901, _("X: Not executed"), \
        _("Process not executed.")
