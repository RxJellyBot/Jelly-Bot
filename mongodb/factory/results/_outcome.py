from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagPrefixedDoubleEnum


class BaseOutcome(FlagPrefixedDoubleEnum):
    @property
    def code_prefix(self) -> str:
        raise NotImplementedError()

    @classmethod
    def default(cls):
        raise NotImplementedError()

    @staticmethod
    def is_success(result):
        return result < 0


class InsertOutcome(BaseOutcome):
    """
    # SUCCESS
    
    -2xx - Actually Inserted
        -201 - Inserted

    -1xx - Not actually inserted
        -101 - Existed

    -x - Miscellaneous
        -1 - Uncategorized

    ================================

    # FAILED

    1xx - Problems related to the process
        104 - Registering Channel
        105 - Registering OnPlatform User ID
        106 - Registering API User ID
        107 - Connecting OnPlatform User ID
        108 - Connecting API User ID

    2xx - Problems related to the model
        201 - Not Serializable
        202 - Not Acknowledged
        203 - Not Found
        204 - Not Entry
        205 - Invalid

    3xx - Problems related to the field of an model
        301 - Field Readonly
        302 - Field Type Mismatch
        303 - Field Invalid
        304 - Field Casting Failed

    4xx - Problems related to cache
        401 - Missing in Cache, Attempted Insertion
        402 - Missing in Cache, Aborted Insertion

    5xx - Unknown Problems
        501 - Model Construction Unknown
        502 - Insertion Unknown

    9xx - Problems related to execution
        901 - Not executed
        902 - Exception occurred
    """
    @property
    def code_prefix(self) -> str:
        return "I-"

    @classmethod
    def default(cls):
        return InsertOutcome.X_NOT_EXECUTED

    O_INSERTED = \
        -201, _("O: Inserted"), _("The system returned OK with data inserted to the database.")
    O_DATA_EXISTS = \
        -101, _("O: Existed"), _("The system returned OK with data already existed in the database.")
    O_MISC = \
        -1, _("O: Uncategorized"), _("The system returned OK with uncategorized reason.")
    X_ON_REG_CHANNEL = \
        104, _("X: Registering Channel"), \
        _("The insertion was failed while registering the identity of channel.")
    X_ON_REG_ONPLAT = \
        105, _("X: Registering OnPlatform User ID"), \
        _("The insertion was failed while registering the identity of on-platform user.")
    X_ON_REG_API = \
        106, _("X: Registering API User ID"), \
        _("The insertion was failed while registering the identity of API user.")
    X_ON_CONN_ONPLAT = \
        107, _("X: Connecting OnPlatform User ID"), \
        _("The insertion was failed while connecting the identity of on-platform user.")
    X_ON_CONN_API = \
        108, _("X: Connecting API User ID"), \
        _("The insertion was failed while connecting the identity of API user.")
    X_NOT_SERIALIZABLE = \
        201, _("X: Not Serializable"), \
        _("The processed data cannot be serialized.")
    X_NOT_ACKNOWLEDGED = \
        202, _("X: Not Acknowledged"), \
        _("The database did not acknowledge the inserted data.")
    X_NOT_FOUND = \
        203, _("X: Not Found"), \
        _("The condition to update/insert does not match any data in the database.")
    X_NOT_MODEL = \
        204, _("X: Not Model"), \
        _("The processed data is not in the shape of a data model.")
    X_INVALID_MODEL = \
        205, _("X: Invalid Model"), \
        _("Some data of the model is invalid.")
    X_READONLY = \
        301, _("X: Readonly"), \
        _("There are some fields that are being attempted to modify are read-only.")
    X_TYPE_MISMATCH = \
        302, _("X: Type Mismatch"), \
        _("The type of the data to update does not match the type of the field to be modified.")
    X_INVALID_FIELD = \
        303, _("X: Invalid Data"), \
        _("The data to be updated is invalid for the field.")
    X_CASTING_FAILED = \
        304, _("X: Casting Failed"), \
        _("The data cannot be casted to the desired type. Check the datatype of the provided data.")
    X_CACHE_MISSING_ATTEMPTED_INSERT = \
        401, _("X: Missing in Cache, Attempted Insertion"), \
        _("The data was not found and the system has attempted to insert a new data but failed.")
    X_CACHE_MISSING_ABORT_INSERT = \
        402, _("X: Missing in Cache, Aborted Insertion"), \
        _("The data was not found and the system aborted to insert a new data.")
    X_CONSTRUCT_UNKNOWN = \
        501, _("X: Model Construction Unknown"), \
        _("An unknown occurred during the construction of a data model.")
    X_INSERT_UNKNOWN = \
        502, _("X: Insertion Unknown"), \
        _("An unknown occurred while inserting the data.")
    X_NOT_EXECUTED = \
        901, _("X: Not Executed"), \
        _("The insertion process had not been executed.")
    X_EXCEPTION_OCCURRED = \
        902, _("X: Exception Occurred"), \
        _("An exception occurred during execution.")

    @staticmethod
    def is_inserted(result):
        return result < -200

    @staticmethod
    def data_found(result):
        return result < -100


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

    9xx - Problems related to execution
        901 - Not executed
    """
    @property
    def code_prefix(self) -> str:
        return "G-"

    @classmethod
    def default(cls):
        return GetOutcome.X_NOT_EXECUTED

    SUCCESS_CACHE_DB = \
        -2, _("O: From Cache/DB"), \
        _("The data was found in either Cache or Database.")
    SUCCESS_ADDED = \
        -1, _("O: Inserted"), \
        _("The data was not found yet the data has been inserted to the database.")
    X_NOT_FOUND_ATTEMPTED_INSERT = \
        101, _("X: Not Found, Attempted Insertion"), \
        _("The data was not found and the system has attempted to insert a new data but failed.")
    X_NOT_FOUND_ABORTED_INSERT = \
        102, _("X: Not Found, Aborted Insertion"), \
        _("The data was not found and the system aborted to insert a new data.")
    X_NOT_FOUND_FIRST_QUERY = \
        103, _("X: Not found on 1st query"), \
        _("The data was not found for the 1st query.")
    X_NOT_FOUND_SECOND_QUERY = \
        104, _("X: Not found on 2nd query"), \
        _("The data was not found for the 2nd query.")
    X_NO_CONTENT = \
        201, _("X: Empty Content"), \
        _("The content in the parameter is empty.")
    X_NOT_EXECUTED = \
        901, _("X: Not Executed"), \
        _("The acquiring process had not been executed.")


class OperationOutcome(BaseOutcome):
    """
    # SUCCESS

    -1 - Operation Completed

    ================================

    # FAILED

    1xx - Problems related to Token Action
        101 - Token Not Found
        102 - Keys Lacking
        103 - Completion Error

    5xx - Problems related to Model
        501 - Construction Error

    9xx - Problems related to execution
        901 - Not executed
    """
    @property
    def code_prefix(self) -> str:
        return "O-"

    @classmethod
    def default(cls):
        return OperationOutcome.X_NOT_EXECUTED

    SUCCESS_COMPLETED = \
        -1, _("O: Completed"), \
        _("The operation was successfully completed.")
    X_TOKEN_NOT_FOUND = \
        101, _("X: Token Not Found"), \
        _("No enqueued token action found using the specified token.")
    X_KEYS_LACKING = \
        102, _("X: Keys Lacking"), \
        _("There are keys lacking so that the token action cannot be completed.")
    X_COMPLETION_FAILED = \
        103, _("X: Completion Failed"), \
        _("The action completion was failed.")
    X_NO_COMPLETE_ACTION = \
        104, _("X: No Complete Action"), \
        _("No complete action implemented yet for the provided action type.")
    X_COMPLETION_ERROR = \
        105, _("X: Completion Error"), \
        _("An error occurred during action completion process.")
    X_TOKEN_EMPTY = \
        106, _("X: Empty Token"), \
        _("The token is empty.")
    X_COLLATION_ERROR = \
        107, _("X: Collation Error"), \
        _("An error occurred during parameter collation process.")
    X_CONSTRUCTION_ERROR = \
        501, _("X: Construction Error"), \
        _("An error occurred during model construction.")
    X_NOT_EXECUTED = \
        901, _("X: Not Executed"), \
        _("The operation had not been executed.")


class UpdateOutcome(BaseOutcome):
    """
    # SUCCESS

    -1 - Success

    ================================

    # FAILED
    
    1xx - Problems related to Model
        101 - Model not found

    9xx - Problems related to execution
        901 - Not executed
    """
    @property
    def code_prefix(self) -> str:
        return "U-"

    @classmethod
    def default(cls):
        return UpdateOutcome.X_NOT_EXECUTED

    SUCCESS_UPDATED = \
        -1, _("O: Success"), \
        _("The updating operation succeed.")
    X_NOT_FOUND = \
        101, _("X: Not found"), \
        _("The data for updating is not found.")
    X_NOT_EXECUTED = \
        901, _("X: Not Executed"), \
        _("The operation had not been executed.")
