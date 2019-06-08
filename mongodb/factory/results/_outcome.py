from django.utils.translation import gettext_noop as _

from extutils.flags import FlagDoubleEnum


class BaseOutcome(FlagDoubleEnum):
    @staticmethod
    def default():
        raise NotImplementedError()

    @staticmethod
    def is_success(result):
        return result < 0


class InsertOutcome(BaseOutcome):
    """
    Less than 0 - OK

        -2xx - Actually Inserted
            -201 - Inserted

        -1xx - Not actually inserted
            -101 - Existed

        -x - Miscellaneous
            -1 - Uncategorized

    Greater than 0 - Failed

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
            205 - Preserialize Failed

        3xx - Problems related to the field of an model
            301 - Field Readonly
            302 - Field Type Mismatch
            303 - Field Invalid

        4xx - Problems related to cache
            401 - Missing in Cache, Attempted Insertion
            402 - Missing in Cache, Aborted Insertion

        5xx - Unknown Problems
            501 - Model Construction Unknown
            502 - Insertion Unknown

        9xx - Problems related to execution
            901 - Not executed
    """
    @staticmethod
    def default():
        return InsertOutcome.FAILED_NOT_EXECUTED

    SUCCESS_INSERTED = \
        -201, _("OK - Inserted"), _("The system returned OK with data inserted to the database.")
    SUCCESS_DATA_EXISTS = \
        -101, _("OK - Existed"), _("The system returned OK with data already existed in the database.")
    SUCCESS_MISC = \
        -1, _("OK - Uncategorized"), _("The system returned OK with uncategorized reason.")
    FAILED_ON_REG_CHANNEL = \
        104, _("FAIL - Registering Channel"), \
        _("The insertion was failed while registering the identity of channel.")
    FAILED_ON_REG_ONPLAT = \
        105, _("FAIL - Registering OnPlatform User ID"), \
        _("The insertion was failed while registering the identity of on-platform user.")
    FAILED_ON_REG_API = \
        106, _("FAIL - Registering API User ID"), \
        _("The insertion was failed while registering the identity of API user.")
    FAILED_ON_CONN_ONPLAT = \
        107, _("FAIL - Connecting OnPlatform User ID"), \
        _("The insertion was failed while connecting the identity of on-platform user.")
    FAILED_ON_CONN_API = \
        108, _("FAIL - Connecting API User ID"), \
        _("The insertion was failed while connecting the identity of API user.")
    FAILED_NOT_SERIALIZABLE = \
        201, _("FAIL - Not Serializable"), \
        _("The processed data cannot be serialized.")
    FAILED_NOT_ACKNOWLEDGED = \
        202, _("FAIL - Not Acknowledged"), \
        _("The database did not acknowledge the inserted data.")
    FAILED_NOT_FOUND = \
        203, _("FAIL - Not Found"), \
        _("The condition to update/insert does not match any data in the database.")
    FAILED_NOT_MODEL = \
        204, _("FAIL - Not Entry"), \
        _("The processed data is not in the shape of a data model.")
    FAILED_PRE_SERIALIZE_FAILED = \
        204, _("FAIL - Pre-serialization Failed"), \
        _("The pre-serialization process failed.")
    FAILED_READONLY = \
        301, _("FAIL - Readonly"), \
        _("There are some fields that are being attempted to modify are read-only.")
    FAILED_TYPE_MISMATCH = \
        302, _("FAIL - Type Mismatch"), \
        _("The type of the data to update does not match the type of the field to be modified.")
    FAILED_INVALID = \
        303, _("FAIL - Invalid Data"), \
        _("The data to be updated is invalid for the field.")
    FAILED_CACHE_MISSING_ATTEMPTED_INSERT = \
        401, _("FAIL - Missing in Cache, Attempted Insertion"), \
        _("The data was not found and the system has attempted to insert a new data but failed.")
    FAILED_CACHE_MISSING_ABORT_INSERT = \
        402, _("FAIL - Missing in Cache, Aborted Insertion"), \
        _("The data was not found and the system aborted to insert a new data.")
    FAILED_CONSTRUCT_UNKNOWN = \
        501, _("FAIL - Model Construction Unknown"), \
        _("An unknown occurred during the construction of a data model.")
    FAILED_INSERT_UNKNOWN = \
        502, _("FAIL - Insertion Unknown"), \
        _("An unknown occurred while inserting the data.")
    FAILED_NOT_EXECUTED = \
        901, _("FAIL - Not Executed"), \
        _("The insertion process had not been executed.")

    @staticmethod
    def is_inserted(result):
        return result < -200

    @staticmethod
    def data_found(result):
        return result < -100


class GetOutcome(BaseOutcome):
    @staticmethod
    def default():
        return InsertOutcome.FAILED_NOT_EXECUTED

    SUCCESS_CACHE_DB = \
        -2, _("OK - From Cache/DB"), \
        _("The data was found.")
    SUCCESS_ADDED = \
        -1, _("OK - Inserted"), \
        _("The data was not found yet the data has been inserted to the database.")
    FAILED_NOT_FOUND_ATTEMPTED_INSERT = \
        1201, _("FAIL - Not Found, Attempted Insertion"), \
        _("The data was not found and the system has attempted to insert a new data but failed.")
    FAILED_NOT_FOUND_ABORTED_INSERT = \
        1202, _("FAIL - Not Found, Aborted Insertion"), \
        _("The data was not found and the system did not attempt to insert a new data.")
    FAILED_NOT_EXECUTED = \
        1901, _("FAIL - Not Executed"), \
        _("The acquiring process had not been executed.")
