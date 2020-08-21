from mongodb.factory.results import WriteOutcome, GetOutcome, UpdateOutcome, OperationOutcome
from tests.base import TestCase

__all__ = ("TestMongoDBOutcome",)


class TestMongoDBOutcome(TestCase):
    def test_write_outcome_code(self):
        self.assertEqual(WriteOutcome.default(), WriteOutcome.X_NOT_EXECUTED)

        for wo in WriteOutcome:
            with self.subTest(wo):
                self.assertEqual(wo.code_prefix, "W")
                self.assertEqual(wo.code_str, f"W-{wo.code}")

    def test_write_outcome_is_inserted(self):
        outcome_data = {
            WriteOutcome.O_INSERTED: True,
            WriteOutcome.O_UPDATED: False,
            WriteOutcome.O_DATA_EXISTS: False,
            WriteOutcome.O_MISC: False,
            WriteOutcome.X_INSUFFICIENT_PERMISSION: False,
            WriteOutcome.X_CHANNEL_TYPE_UNKNOWN: False,
            WriteOutcome.X_PINNED_CONTENT_EXISTED: False,
            WriteOutcome.X_ON_REG_CHANNEL: False,
            WriteOutcome.X_ON_REG_ONPLAT: False,
            WriteOutcome.X_ON_REG_API: False,
            WriteOutcome.X_ON_CONN_ONPLAT: False,
            WriteOutcome.X_ON_CONN_API: False,
            WriteOutcome.X_ON_SET_CONFIG: False,
            WriteOutcome.X_INVALID_URL: False,
            WriteOutcome.X_AR_INVALID_KEYWORD: False,
            WriteOutcome.X_AR_INVALID_RESPONSE: False,
            WriteOutcome.X_CNL_DEFAULT_CREATE_FAILED: False,
            WriteOutcome.X_EMPTY_CONTENT: False,
            WriteOutcome.X_UNKNOWN_EXECODE_ACTION: False,
            WriteOutcome.X_NOT_SERIALIZABLE: False,
            WriteOutcome.X_NOT_ACKNOWLEDGED: False,
            WriteOutcome.X_NOT_MODEL: False,
            WriteOutcome.X_INVALID_MODEL: False,
            WriteOutcome.X_MODEL_KEY_NOT_EXIST: False,
            WriteOutcome.X_READONLY: False,
            WriteOutcome.X_TYPE_MISMATCH: False,
            WriteOutcome.X_INVALID_FIELD_VALUE: False,
            WriteOutcome.X_CASTING_FAILED: False,
            WriteOutcome.X_REQUIRED_NOT_FILLED: False,
            WriteOutcome.X_INVALID_MODEL_FIELD: False,
            WriteOutcome.X_NOT_FOUND_ATTEMPTED_INSERT: False,
            WriteOutcome.X_NOT_FOUND_ABORTED_INSERT: False,
            WriteOutcome.X_CHANNEL_NOT_FOUND: False,
            WriteOutcome.X_NO_MODEL_CLASS: False,
            WriteOutcome.X_CONSTRUCT_UNKNOWN: False,
            WriteOutcome.X_INSERT_UNKNOWN: False,
            WriteOutcome.X_NOT_EXECUTED: False,
            WriteOutcome.X_EXCEPTION_OCCURRED: False
        }

        for wo, expected in outcome_data.items():
            with self.subTest(code=wo, expected=expected):
                self.assertEqual(wo.is_inserted, expected)

    def test_write_outcome_data_found(self):
        outcome_data = {
            WriteOutcome.O_INSERTED: False,
            WriteOutcome.O_UPDATED: True,
            WriteOutcome.O_DATA_EXISTS: True,
            WriteOutcome.O_MISC: False,
            WriteOutcome.X_INSUFFICIENT_PERMISSION: False,
            WriteOutcome.X_CHANNEL_TYPE_UNKNOWN: False,
            WriteOutcome.X_PINNED_CONTENT_EXISTED: False,
            WriteOutcome.X_ON_REG_CHANNEL: False,
            WriteOutcome.X_ON_REG_ONPLAT: False,
            WriteOutcome.X_ON_REG_API: False,
            WriteOutcome.X_ON_CONN_ONPLAT: False,
            WriteOutcome.X_ON_CONN_API: False,
            WriteOutcome.X_ON_SET_CONFIG: False,
            WriteOutcome.X_INVALID_URL: False,
            WriteOutcome.X_AR_INVALID_KEYWORD: False,
            WriteOutcome.X_AR_INVALID_RESPONSE: False,
            WriteOutcome.X_CNL_DEFAULT_CREATE_FAILED: False,
            WriteOutcome.X_EMPTY_CONTENT: False,
            WriteOutcome.X_UNKNOWN_EXECODE_ACTION: False,
            WriteOutcome.X_NOT_SERIALIZABLE: False,
            WriteOutcome.X_NOT_ACKNOWLEDGED: False,
            WriteOutcome.X_NOT_MODEL: False,
            WriteOutcome.X_INVALID_MODEL: False,
            WriteOutcome.X_MODEL_KEY_NOT_EXIST: False,
            WriteOutcome.X_READONLY: False,
            WriteOutcome.X_TYPE_MISMATCH: False,
            WriteOutcome.X_INVALID_FIELD_VALUE: False,
            WriteOutcome.X_CASTING_FAILED: False,
            WriteOutcome.X_REQUIRED_NOT_FILLED: False,
            WriteOutcome.X_INVALID_MODEL_FIELD: False,
            WriteOutcome.X_NOT_FOUND_ATTEMPTED_INSERT: False,
            WriteOutcome.X_NOT_FOUND_ABORTED_INSERT: False,
            WriteOutcome.X_CHANNEL_NOT_FOUND: False,
            WriteOutcome.X_NO_MODEL_CLASS: False,
            WriteOutcome.X_CONSTRUCT_UNKNOWN: False,
            WriteOutcome.X_INSERT_UNKNOWN: False,
            WriteOutcome.X_NOT_EXECUTED: False,
            WriteOutcome.X_EXCEPTION_OCCURRED: False
        }

        for wo, expected in outcome_data.items():
            with self.subTest(code=wo, expected=expected):
                self.assertEqual(wo.data_found, expected)

    def test_write_outcome_is_success(self):
        outcome_data = {
            WriteOutcome.O_INSERTED: True,
            WriteOutcome.O_UPDATED: True,
            WriteOutcome.O_DATA_EXISTS: True,
            WriteOutcome.O_MISC: True,
            WriteOutcome.X_INSUFFICIENT_PERMISSION: False,
            WriteOutcome.X_CHANNEL_TYPE_UNKNOWN: False,
            WriteOutcome.X_PINNED_CONTENT_EXISTED: False,
            WriteOutcome.X_ON_REG_CHANNEL: False,
            WriteOutcome.X_ON_REG_ONPLAT: False,
            WriteOutcome.X_ON_REG_API: False,
            WriteOutcome.X_ON_CONN_ONPLAT: False,
            WriteOutcome.X_ON_CONN_API: False,
            WriteOutcome.X_ON_SET_CONFIG: False,
            WriteOutcome.X_INVALID_URL: False,
            WriteOutcome.X_AR_INVALID_KEYWORD: False,
            WriteOutcome.X_AR_INVALID_RESPONSE: False,
            WriteOutcome.X_CNL_DEFAULT_CREATE_FAILED: False,
            WriteOutcome.X_EMPTY_CONTENT: False,
            WriteOutcome.X_UNKNOWN_EXECODE_ACTION: False,
            WriteOutcome.X_NOT_SERIALIZABLE: False,
            WriteOutcome.X_NOT_ACKNOWLEDGED: False,
            WriteOutcome.X_NOT_MODEL: False,
            WriteOutcome.X_INVALID_MODEL: False,
            WriteOutcome.X_MODEL_KEY_NOT_EXIST: False,
            WriteOutcome.X_READONLY: False,
            WriteOutcome.X_TYPE_MISMATCH: False,
            WriteOutcome.X_INVALID_FIELD_VALUE: False,
            WriteOutcome.X_CASTING_FAILED: False,
            WriteOutcome.X_REQUIRED_NOT_FILLED: False,
            WriteOutcome.X_INVALID_MODEL_FIELD: False,
            WriteOutcome.X_NOT_FOUND_ATTEMPTED_INSERT: False,
            WriteOutcome.X_NOT_FOUND_ABORTED_INSERT: False,
            WriteOutcome.X_CHANNEL_NOT_FOUND: False,
            WriteOutcome.X_NO_MODEL_CLASS: False,
            WriteOutcome.X_CONSTRUCT_UNKNOWN: False,
            WriteOutcome.X_INSERT_UNKNOWN: False,
            WriteOutcome.X_NOT_EXECUTED: False,
            WriteOutcome.X_EXCEPTION_OCCURRED: False
        }

        for wo, expected in outcome_data.items():
            with self.subTest(code=wo, expected=expected):
                self.assertEqual(wo.is_success, expected)

    def test_get_outcome_code(self):
        self.assertEqual(GetOutcome.default(), GetOutcome.X_NOT_EXECUTED)

        for go in GetOutcome:
            with self.subTest(go):
                self.assertEqual(go.code_prefix, "G")
                self.assertEqual(go.code_str, f"G-{go.code}")

    def test_get_outcome_is_success(self):
        outcome_data = {
            GetOutcome.O_CACHE_DB: True,
            GetOutcome.O_ADDED: True,
            GetOutcome.X_NOT_FOUND_ATTEMPTED_INSERT: False,
            GetOutcome.X_NOT_FOUND_ABORTED_INSERT: False,
            GetOutcome.X_NOT_FOUND_FIRST_QUERY: False,
            GetOutcome.X_NOT_FOUND_SECOND_QUERY: False,
            GetOutcome.X_NO_CONTENT: False,
            GetOutcome.X_CHANNEL_NOT_FOUND: False,
            GetOutcome.X_CHANNEL_CONFIG_ERROR: False,
            GetOutcome.X_DEFAULT_PROFILE_ERROR: False,
            GetOutcome.X_EXECODE_TYPE_MISMATCH: False,
            GetOutcome.X_NOT_EXECUTED: False,
        }

        for go, expected in outcome_data.items():
            with self.subTest(code=go, expected=expected):
                self.assertEqual(go.is_success, expected)

    def test_update_outcome_code(self):
        self.assertEqual(UpdateOutcome.default(), UpdateOutcome.X_NOT_EXECUTED)

        for uo in UpdateOutcome:
            with self.subTest(uo):
                self.assertEqual(uo.code_prefix, "U")
                self.assertEqual(uo.code_str, f"U-{uo.code}")

    def test_update_outcome_is_success(self):
        outcome_data = {
            UpdateOutcome.O_FOUND: True,
            UpdateOutcome.O_PARTIAL_ARGS_REMOVED: True,
            UpdateOutcome.O_PARTIAL_ARGS_INVALID: True,
            UpdateOutcome.O_UPDATED: True,
            UpdateOutcome.X_NOT_FOUND: False,
            UpdateOutcome.X_ARGS_PARSE_FAILED: False,
            UpdateOutcome.X_UNEDITABLE: False,
            UpdateOutcome.X_CHANNEL_NOT_FOUND: False,
            UpdateOutcome.X_CONFIG_NOT_EXISTS: False,
            UpdateOutcome.X_CONFIG_TYPE_MISMATCH: False,
            UpdateOutcome.X_CONFIG_VALUE_INVALID: False,
            UpdateOutcome.X_INSUFFICIENT_PERMISSION: False,
            UpdateOutcome.X_NOT_EXECUTED: False,
        }

        for uo, expected in outcome_data.items():
            with self.subTest(code=uo, expected=expected):
                self.assertEqual(uo.is_success, expected)

    def test_operation_outcome_code(self):
        self.assertEqual(OperationOutcome.default(), OperationOutcome.X_NOT_EXECUTED)

        for oo in OperationOutcome:
            with self.subTest(oo):
                self.assertEqual(oo.code_prefix, "O")
                self.assertEqual(oo.code_str, f"O-{oo.code}")

    def test_operation_outcome_is_success(self):
        outcome_data = {
            OperationOutcome.O_ADDL_ARGS_OMITTED: True,
            OperationOutcome.O_READONLY_ARGS_OMITTED: True,
            OperationOutcome.O_COMPLETED: True,
            OperationOutcome.X_EXECODE_NOT_FOUND: False,
            OperationOutcome.X_MISSING_ARGS: False,
            OperationOutcome.X_COMPLETION_FAILED: False,
            OperationOutcome.X_NO_COMPLETE_ACTION: False,
            OperationOutcome.X_COMPLETION_ERROR: False,
            OperationOutcome.X_EXECODE_EMPTY: False,
            OperationOutcome.X_COLLATION_ERROR: False,
            OperationOutcome.X_EXECODE_TYPE_MISMATCH: False,
            OperationOutcome.X_CHANNEL_NOT_FOUND: False,
            OperationOutcome.X_SAME_SRC_DEST: False,
            OperationOutcome.X_SRC_DATA_NOT_FOUND: False,
            OperationOutcome.X_DEST_DATA_NOT_FOUND: False,
            OperationOutcome.X_INSUFFICIENT_PERMISSION: False,
            OperationOutcome.X_UNATTACHABLE: False,
            OperationOutcome.X_NO_ATTACHABLE_PROFILES: False,
            OperationOutcome.X_PROFILE_NOT_FOUND_NAME: False,
            OperationOutcome.X_PROFILE_NOT_FOUND_OID: False,
            OperationOutcome.X_EXECUTOR_NOT_IN_CHANNEL: False,
            OperationOutcome.X_TARGET_NOT_IN_CHANNEL: False,
            OperationOutcome.X_DETACH_FAILED: False,
            OperationOutcome.X_INVALID_PERM_LV: False,
            OperationOutcome.X_INVALID_COLOR: False,
            OperationOutcome.X_INVALID_CHANNEL_OID: False,
            OperationOutcome.X_EMPTY_ARGS: False,
            OperationOutcome.X_MISSING_CHANNEL_OID: False,
            OperationOutcome.X_CONSTRUCTION_ERROR: False,
            OperationOutcome.X_VALUE_TYPE_MISMATCH: False,
            OperationOutcome.X_VALUE_INVALID: False,
            OperationOutcome.X_NOT_EXECUTED: False,
            OperationOutcome.X_NOT_UPDATED: False,
            OperationOutcome.X_NOT_DELETED: False,
            OperationOutcome.X_INTEGRATION_FAILED: False,
            OperationOutcome.X_ERROR: False
        }

        for oo, expected in outcome_data.items():
            with self.subTest(code=oo, expected=expected):
                self.assertEqual(oo.is_success, expected)
