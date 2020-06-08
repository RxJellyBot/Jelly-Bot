from bson import ObjectId

from extutils.dt import now_utc_aware
from flags import Execode, ExecodeCompletionOutcome, AutoReplyContentType, Platform
from JellyBot.api.static import param
from models import ExecodeEntryModel, AutoReplyModuleExecodeModel, AutoReplyContentModel, AutoReplyModuleModel
from mongodb.exceptions import NoCompleteActionError
from mongodb.factory.ar_conn import AutoReplyModuleManager
from mongodb.factory import ChannelManager, ExecodeManager, RootUserManager
from mongodb.factory.results import WriteOutcome, GetOutcome, OperationOutcome
from tests.base import TestDatabaseMixin, TestModelMixin, TestTimeComparisonMixin

__all__ = ["TestExecodeManager", "TestExecodeManagerComplete"]


class TestExecodeManager(TestModelMixin, TestTimeComparisonMixin, TestDatabaseMixin):
    CREATOR_OID = ObjectId()
    CREATOR_OID_2 = ObjectId()

    @staticmethod
    def collections_to_reset():
        return [ExecodeManager]

    def test_add_duplicate(self):
        self.assertEqual(
            ExecodeManager.insert_one_model(ExecodeEntryModel(
                CreatorOid=ObjectId(), Execode="A" * ExecodeEntryModel.EXECODE_LENGTH, ActionType=Execode.SYS_TEST,
                Timestamp=now_utc_aware(for_mongo=True)
            ))[0],
            WriteOutcome.O_INSERTED
        )
        self.assertEqual(
            ExecodeManager.insert_one_model(ExecodeEntryModel(
                CreatorOid=ObjectId(), Execode="A" * ExecodeEntryModel.EXECODE_LENGTH, ActionType=Execode.SYS_TEST,
                Timestamp=now_utc_aware(for_mongo=True)
            ))[0],
            WriteOutcome.O_DATA_EXISTS
        )

    def test_enqueue_action(self):
        now = now_utc_aware()
        result = ExecodeManager.enqueue_execode(self.CREATOR_OID, Execode.REGISTER_CHANNEL)

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertModelEqual(
            result.model,
            ExecodeEntryModel(
                CreatorOid=self.CREATOR_OID, Execode=result.execode, ActionType=Execode.REGISTER_CHANNEL,
                Timestamp=result.model.timestamp
            ))
        self.assertTimeDifferenceLessEqual(now, result.model.timestamp, 1)

        self.assertEqual(ExecodeManager.count_documents({}), 1)

    def test_enqueue_with_model(self):
        now = now_utc_aware()
        result = ExecodeManager.enqueue_execode(
            self.CREATOR_OID, Execode.AR_ADD, AutoReplyModuleExecodeModel,
            Keyword=AutoReplyContentModel(Content="A"), Responses=[AutoReplyContentModel(Content="B")])

        expected_data = AutoReplyModuleExecodeModel(Keyword=AutoReplyContentModel(Content="A"),
                                                    Responses=[AutoReplyContentModel(Content="B")])

        self.assertEqual(result.outcome, WriteOutcome.O_INSERTED)
        self.assertTrue(result.success)
        self.assertModelEqual(
            result.model,
            ExecodeEntryModel(
                CreatorOid=self.CREATOR_OID, Execode=result.execode, ActionType=Execode.AR_ADD,
                Timestamp=result.model.timestamp, Data=expected_data.to_json()
            ))
        self.assertTimeDifferenceLessEqual(now, result.model.timestamp, 1)

        self.assertEqual(ExecodeManager.count_documents({}), 1)

    def test_enqueue_no_model_class(self):
        result = ExecodeManager.enqueue_execode(self.CREATOR_OID, Execode.REGISTER_CHANNEL, A="B")

        self.assertEqual(result.outcome, WriteOutcome.X_NO_MODEL_CLASS)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self.assertEqual(ExecodeManager.count_documents({}), 0)

    def test_enqueue_invalid_model(self):
        result = ExecodeManager.enqueue_execode(self.CREATOR_OID, Execode.AR_ADD, AutoReplyModuleExecodeModel,
                                                Keyword="A")

        self.assertEqual(result.outcome, WriteOutcome.X_INVALID_MODEL)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self.assertEqual(ExecodeManager.count_documents({}), 0)

    def test_enqueue_unknown_action(self):
        result = ExecodeManager.enqueue_execode(self.CREATOR_OID, Execode.UNKNOWN)

        self.assertEqual(result.outcome, WriteOutcome.X_ACTION_UNKNOWN)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self.assertEqual(ExecodeManager.count_documents({}), 0)

    def test_get_list(self):
        expected = set()

        for _ in range(5):
            mdl = ExecodeEntryModel(CreatorOid=self.CREATOR_OID, Execode=ExecodeManager.generate_hex_token(),
                                    ActionType=Execode.REGISTER_CHANNEL, Timestamp=now_utc_aware(for_mongo=True))
            ExecodeManager.insert_one_model(mdl)
            expected.add(mdl)

        for _ in range(3):
            mdl = ExecodeEntryModel(CreatorOid=self.CREATOR_OID_2, Execode=ExecodeManager.generate_hex_token(),
                                    ActionType=Execode.REGISTER_CHANNEL, Timestamp=now_utc_aware(for_mongo=True))
            ExecodeManager.insert_one_model(mdl)

        self.assertModelSetEqual(set(list(ExecodeManager.get_queued_execodes(self.CREATOR_OID))), set(expected))
        self.assertEqual(ExecodeManager.count_documents({}), 8)
        self.assertEqual(ExecodeManager.count_documents({ExecodeEntryModel.CreatorOid.key: self.CREATOR_OID}), 5)
        self.assertEqual(ExecodeManager.count_documents({ExecodeEntryModel.CreatorOid.key: self.CREATOR_OID_2}), 3)

    def test_get_list_no_exists(self):
        self.assertEqual(list(ExecodeManager.get_queued_execodes(self.CREATOR_OID)), [])
        self.assertEqual(ExecodeManager.count_documents({}), 0)

    def test_get_entry(self):
        execode = ExecodeManager.generate_hex_token()

        mdl = ExecodeEntryModel(CreatorOid=self.CREATOR_OID_2, Execode=execode,
                                ActionType=Execode.REGISTER_CHANNEL, Timestamp=now_utc_aware(for_mongo=True))

        ExecodeManager.insert_one_model(mdl)

        result = ExecodeManager.get_execode_entry(execode)

        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, mdl)

        self.assertEqual(ExecodeManager.count_documents({}), 1)

    def test_get_entry_not_exists(self):
        result = ExecodeManager.get_execode_entry(ExecodeManager.generate_hex_token(), Execode.REGISTER_CHANNEL)

        self.assertEqual(result.outcome, GetOutcome.X_NOT_FOUND_ABORTED_INSERT)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

    def test_get_entry_with_action(self):
        execode = ExecodeManager.generate_hex_token()

        mdl = ExecodeEntryModel(CreatorOid=self.CREATOR_OID_2, Execode=execode,
                                ActionType=Execode.REGISTER_CHANNEL, Timestamp=now_utc_aware(for_mongo=True))

        ExecodeManager.insert_one_model(mdl)

        result = ExecodeManager.get_execode_entry(execode, Execode.REGISTER_CHANNEL)

        self.assertEqual(result.outcome, GetOutcome.O_CACHE_DB)
        self.assertTrue(result.success)
        self.assertModelEqual(result.model, mdl)

        self.assertEqual(ExecodeManager.count_documents({}), 1)

    def test_get_entry_action_mismatch(self):
        execode = ExecodeManager.generate_hex_token()

        mdl = ExecodeEntryModel(CreatorOid=self.CREATOR_OID_2, Execode=execode,
                                ActionType=Execode.REGISTER_CHANNEL, Timestamp=now_utc_aware(for_mongo=True))

        ExecodeManager.insert_one_model(mdl)

        result = ExecodeManager.get_execode_entry(execode, Execode.AR_ADD)

        self.assertEqual(result.outcome, GetOutcome.X_EXECODE_TYPE_MISMATCH)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self.assertEqual(ExecodeManager.count_documents({}), 1)

    def test_get_entry_code_mismatch(self):
        mdl = ExecodeEntryModel(CreatorOid=self.CREATOR_OID_2, Execode=ExecodeManager.generate_hex_token(),
                                ActionType=Execode.REGISTER_CHANNEL, Timestamp=now_utc_aware(for_mongo=True))

        ExecodeManager.insert_one_model(mdl)

        result = ExecodeManager.get_execode_entry("A", Execode.AR_ADD)

        self.assertEqual(result.outcome, GetOutcome.X_NOT_FOUND_ABORTED_INSERT)
        self.assertFalse(result.success)
        self.assertIsNone(result.model)

        self.assertEqual(ExecodeManager.count_documents({}), 1)

    def test_del(self):
        execode = ExecodeManager.generate_hex_token()

        mdl = ExecodeEntryModel(CreatorOid=self.CREATOR_OID_2, Execode=execode,
                                ActionType=Execode.REGISTER_CHANNEL, Timestamp=now_utc_aware(for_mongo=True))

        ExecodeManager.insert_one_model(mdl)
        self.assertEqual(ExecodeManager.count_documents({}), 1)

        ExecodeManager.remove_execode(execode)
        self.assertEqual(ExecodeManager.count_documents({}), 0)

    def test_del_not_exists(self):
        self.assertEqual(ExecodeManager.count_documents({}), 0)
        ExecodeManager.remove_execode(ExecodeManager.generate_hex_token())
        self.assertEqual(ExecodeManager.count_documents({}), 0)


class TestExecodeManagerComplete(TestModelMixin, TestDatabaseMixin):
    inst = None

    @staticmethod
    def collections_to_reset():
        return [ExecodeManager, AutoReplyModuleManager, ChannelManager, RootUserManager]

    def test_ar_add_new(self):
        enqueue = ExecodeManager.enqueue_execode(
            ObjectId(), Execode.AR_ADD, AutoReplyModuleExecodeModel,
            Keyword=AutoReplyContentModel(Content="A"), Responses=[AutoReplyContentModel(Content="B")])
        code = enqueue.execode
        mdl = enqueue.model

        result = ExecodeManager.complete_execode(
            code, {param.AutoReply.PLATFORM: "1", param.AutoReply.CHANNEL_TOKEN: "U123456"})

        self.assertEqual(result.outcome, OperationOutcome.O_COMPLETED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, mdl)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.O_OK)

        self.assertEqual(ChannelManager.count_documents({}), 1)
        self.assertEqual(AutoReplyModuleManager.count_documents({}), 1)

    def test_ar_add_invalid(self):
        enqueue = ExecodeManager.enqueue_execode(
            ObjectId(), Execode.AR_ADD, AutoReplyModuleExecodeModel,
            Keyword=AutoReplyContentModel(Content="87", ContentType=AutoReplyContentType.LINE_STICKER),
            Responses=[AutoReplyContentModel(Content="B")])
        code = enqueue.execode

        result = ExecodeManager.complete_execode(
            code, {param.AutoReply.PLATFORM: "1", param.AutoReply.CHANNEL_TOKEN: "U123456"})

        self.assertEqual(result.outcome, OperationOutcome.X_COMPLETION_FAILED)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.X_AR_REGISTER_MODULE)

        self.assertEqual(ChannelManager.count_documents({}), 1)
        self.assertEqual(AutoReplyModuleManager.count_documents({}), 0)

    def test_register_channel_new(self):
        enqueue = ExecodeManager.enqueue_execode(ObjectId(), Execode.REGISTER_CHANNEL)
        code = enqueue.execode
        mdl = enqueue.model

        result = ExecodeManager.complete_execode(
            code, {param.AutoReply.PLATFORM: "1", param.AutoReply.CHANNEL_TOKEN: "U123456"})

        self.assertEqual(result.outcome, OperationOutcome.O_COMPLETED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, mdl)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.O_OK)

        self.assertEqual(ChannelManager.count_documents({}), 1)

    def test_register_channel_existed(self):
        self.assertTrue(ChannelManager.ensure_register(Platform.LINE, "U123456").success)

        enqueue = ExecodeManager.enqueue_execode(ObjectId(), Execode.REGISTER_CHANNEL)
        code = enqueue.execode
        mdl = enqueue.model

        result = ExecodeManager.complete_execode(
            code, {param.AutoReply.PLATFORM: "1", param.AutoReply.CHANNEL_TOKEN: "U123456"})

        self.assertEqual(result.outcome, OperationOutcome.O_COMPLETED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, mdl)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.O_OK)

        self.assertEqual(ChannelManager.count_documents({}), 1)

    def test_register_channel_platform_error(self):
        enqueue = ExecodeManager.enqueue_execode(ObjectId(), Execode.REGISTER_CHANNEL)
        code = enqueue.execode

        result = ExecodeManager.complete_execode(
            code, {param.AutoReply.PLATFORM: "99999", param.AutoReply.CHANNEL_TOKEN: "U123456"})

        self.assertEqual(result.outcome, OperationOutcome.X_COMPLETION_FAILED)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.X_IDT_CHANNEL_ERROR)

        self.assertEqual(ChannelManager.count_documents({}), 0)

    def _user_integrate_pre(self, reg_1, reg_2):
        channel_oid = ObjectId()

        if reg_1:
            creator_oid_result = RootUserManager.register_onplat(Platform.LINE, "U123456789")
            self.assertTrue(creator_oid_result.success)
            creator_oid = creator_oid_result.model.id
        else:
            creator_oid = ObjectId()

        if reg_2:
            creator_oid_2_result = RootUserManager.register_onplat(Platform.LINE, "U12345678A")
            self.assertTrue(creator_oid_2_result.success)
            creator_oid_2 = creator_oid_2_result.model.id
        else:
            creator_oid_2 = ObjectId()

        AutoReplyModuleManager.insert_one_model(
            AutoReplyModuleModel(
                Keyword=AutoReplyContentModel(Content="A"), Responses=[AutoReplyContentModel(Content="B")],
                CreatorOid=creator_oid, ChannelOid=channel_oid))
        self.assertEqual(AutoReplyModuleManager.count_documents({}), 1)
        self.assertEqual(AutoReplyModuleManager.count_documents({AutoReplyModuleModel.CreatorOid.key: creator_oid}), 1)

        return creator_oid, creator_oid_2

    def _user_integrate_post(self, creator_oid, creator_oid_2, migrated):
        if migrated:
            self.assertEqual(
                AutoReplyModuleManager.count_documents({AutoReplyModuleModel.CreatorOid.key: creator_oid}), 0)
            self.assertEqual(
                AutoReplyModuleManager.count_documents({AutoReplyModuleModel.CreatorOid.key: creator_oid_2}), 1)
        else:
            self.assertEqual(
                AutoReplyModuleManager.count_documents({AutoReplyModuleModel.CreatorOid.key: creator_oid}), 1)
            self.assertEqual(
                AutoReplyModuleManager.count_documents({AutoReplyModuleModel.CreatorOid.key: creator_oid_2}), 0)

    def test_user_integrate(self):
        creator_oid, creator_oid_2 = self._user_integrate_pre(True, True)

        enqueue = ExecodeManager.enqueue_execode(creator_oid, Execode.INTEGRATE_USER_DATA)

        result = ExecodeManager.complete_execode(enqueue.execode, {param.Execode.USER_OID: str(creator_oid_2)})

        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.O_OK)
        self.assertEqual(result.outcome, OperationOutcome.O_COMPLETED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, set())

        self._user_integrate_post(creator_oid, creator_oid_2, True)

    def test_user_integrate_src_eq_dest(self):
        creator_oid, _ = self._user_integrate_pre(True, False)

        enqueue = ExecodeManager.enqueue_execode(creator_oid, Execode.INTEGRATE_USER_DATA)

        result = ExecodeManager.complete_execode(enqueue.execode, {param.Execode.USER_OID: str(creator_oid)})

        self.assertEqual(result.outcome, OperationOutcome.X_COMPLETION_FAILED)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.X_IDT_SOURCE_EQ_TARGET)

    def test_user_integrate_src_exist_only(self):
        creator_oid, creator_oid_2 = self._user_integrate_pre(True, False)

        enqueue = ExecodeManager.enqueue_execode(creator_oid, Execode.INTEGRATE_USER_DATA)

        result = ExecodeManager.complete_execode(enqueue.execode, {param.Execode.USER_OID: str(creator_oid_2)})

        self.assertEqual(result.outcome, OperationOutcome.X_COMPLETION_FAILED)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.X_IDT_TARGET_NOT_FOUND)

        self._user_integrate_post(creator_oid, creator_oid_2, False)

    def test_user_integrate_dest_exist_only(self):
        creator_oid, creator_oid_2 = self._user_integrate_pre(False, True)

        enqueue = ExecodeManager.enqueue_execode(creator_oid, Execode.INTEGRATE_USER_DATA)

        result = ExecodeManager.complete_execode(enqueue.execode, {param.Execode.USER_OID: str(creator_oid_2)})

        self.assertEqual(result.outcome, OperationOutcome.X_COMPLETION_FAILED)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.X_IDT_SOURCE_NOT_FOUND)

        self._user_integrate_post(creator_oid, creator_oid_2, False)

    def test_user_integrate_not_exists(self):
        creator_oid, creator_oid_2 = self._user_integrate_pre(False, False)

        enqueue = ExecodeManager.enqueue_execode(creator_oid, Execode.INTEGRATE_USER_DATA)

        result = ExecodeManager.complete_execode(enqueue.execode, {param.Execode.USER_OID: str(creator_oid_2)})

        self.assertEqual(result.outcome, OperationOutcome.X_COMPLETION_FAILED)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.X_IDT_SOURCE_NOT_FOUND)

        self._user_integrate_post(creator_oid, creator_oid_2, False)

    def test_unhandled_action(self):
        enqueue = ExecodeManager.enqueue_execode(ObjectId(), Execode.SYS_TEST)

        result = ExecodeManager.complete_execode(enqueue.execode, {})

        self.assertEqual(result.outcome, OperationOutcome.X_NO_COMPLETE_ACTION)
        self.assertFalse(result.success)
        self.assertIsInstance(result.exception, NoCompleteActionError)
        self.assertEqual(result.exception.action, Execode.SYS_TEST)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.X_NOT_EXECUTED)

    def test_complete_additional_kwargs(self):
        enqueue = ExecodeManager.enqueue_execode(ObjectId(), Execode.REGISTER_CHANNEL)

        result = ExecodeManager.complete_execode(
            enqueue.execode, {param.AutoReply.PLATFORM: "1", param.AutoReply.CHANNEL_TOKEN: "U123456", "A": "B"})

        self.assertEqual(result.outcome, OperationOutcome.O_COMPLETED)
        self.assertTrue(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, set())
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.O_OK)

        self.assertEqual(ChannelManager.count_documents({}), 1)

    def test_complete_missing_kwargs(self):
        enqueue = ExecodeManager.enqueue_execode(ObjectId(), Execode.REGISTER_CHANNEL)

        result = ExecodeManager.complete_execode(
            enqueue.execode, {param.AutoReply.PLATFORM: "1"})

        self.assertEqual(result.outcome, OperationOutcome.X_ARGS_LACKING)
        self.assertFalse(result.success)
        self.assertIsNone(result.exception)
        self.assertModelEqual(result.model, enqueue.model)
        self.assertEqual(result.lacking_keys, {param.AutoReply.CHANNEL_TOKEN})
        self.assertEqual(result.completion_outcome, ExecodeCompletionOutcome.X_ARGS_LACKING)

        self.assertEqual(ChannelManager.count_documents({}), 0)
