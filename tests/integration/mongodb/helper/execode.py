from bson import ObjectId

from extutils.dt import now_utc_aware
from flags import Execode, ExecodeCompletionOutcome, ExecodeCollationFailedReason, Platform
from JellyBot.api.static import param
from models import ExecodeEntryModel, AutoReplyModuleModel, AutoReplyContentModel, ChannelModel, OID_KEY
from models.exceptions import InvalidModelError
from mongodb.exceptions import ExecodeCollationError, NoCompleteActionError
from mongodb.factory import ChannelManager, RootUserManager
from mongodb.factory.ar_conn import AutoReplyModuleManager
from mongodb.helper import ExecodeCompletor
from tests.base import TestCase

__all__ = ("TestExecodeCompletor",)


class TestExecodeCompletor(TestCase):
    CREATOR_OID = ObjectId()

    EXECODE = "ABCDEFGHIJ"

    @staticmethod
    def obj_to_clear():
        return [ExecodeCompletor, RootUserManager]

    def test_unsupported(self):
        mdl = ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode=self.EXECODE, ActionType=Execode.SYS_TEST,
            Timestamp=now_utc_aware(), Data={}
        )

        with self.assertRaises(NoCompleteActionError):
            ExecodeCompletor.complete_execode(mdl, {})

    def test_ar_add(self):
        mdl = ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode=self.EXECODE, ActionType=Execode.AR_ADD,
            Timestamp=now_utc_aware(), Data={
                "kw": {"c": "KEYWORD", "t": 0},
                "rp": [{"c": "RESPONSE", "t": 0}],
                "p": False,
                "pr": False,
                "cd": 0,
                "t": []
            }
        )

        outcome = ExecodeCompletor.complete_execode(mdl, {param.AutoReply.CHANNEL_TOKEN: "U12345",
                                                          param.AutoReply.PLATFORM: "1"})
        self.assertEqual(outcome, ExecodeCompletionOutcome.O_OK)

        ch_mdl = ChannelManager.get_channel_token(1, "U12345")
        self.assertIsNotNone(ch_mdl)
        self.assertEqual(
            AutoReplyModuleManager.count({
                "kw": {"c": "KEYWORD", "t": 0},
                "rp": [{"c": "RESPONSE", "t": 0}],
                "cr": self.CREATOR_OID,
                "ch": ch_mdl.id,
                "p": False,
                "pr": False,
                "cd": 0,
                "t": []
            }),
            1
        )

    def test_ar_add_collation_empty_param(self):
        mdl = ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode=self.EXECODE, ActionType=Execode.AR_ADD,
            Timestamp=now_utc_aware(), Data={
                AutoReplyModuleModel.Keyword.key: {
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                },
                AutoReplyModuleModel.Responses.key: [{
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                }],
                AutoReplyModuleModel.Pinned.key: False,
                AutoReplyModuleModel.Private.key: False,
                AutoReplyModuleModel.CooldownSec.key: 0,
                AutoReplyModuleModel.TagIds.key: []
            }
        )

        with self.assertRaises(ExecodeCollationError) as ex:
            ExecodeCompletor.complete_execode(mdl, {param.AutoReply.CHANNEL_TOKEN: "U12345",
                                                    param.AutoReply.PLATFORM: ""})

        self.assertEqual(ex.exception.err_code, ExecodeCollationFailedReason.EMPTY_CONTENT)

        self.assertIsNone(ChannelManager.find_one())
        self.assertEqual(
            AutoReplyModuleManager.count({
                AutoReplyModuleModel.Keyword.key: {
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                },
                AutoReplyModuleModel.Responses.key: [{
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                }],
                AutoReplyModuleModel.Pinned.key: False,
                AutoReplyModuleModel.Private.key: False,
                AutoReplyModuleModel.CooldownSec.key: 0,
                AutoReplyModuleModel.TagIds.key: []
            }),
            0
        )

    def test_ar_add_entry_missing_keys(self):
        with self.assertRaises(InvalidModelError):
            ExecodeEntryModel(
                CreatorOid=self.CREATOR_OID, Execode=self.EXECODE, ActionType=Execode.AR_ADD,
                Timestamp=now_utc_aware(), Data={
                    AutoReplyModuleModel.Pinned.key: False,
                    AutoReplyModuleModel.Private.key: False,
                    AutoReplyModuleModel.CooldownSec.key: 0,
                    AutoReplyModuleModel.TagIds.key: []
                }
            )

    def test_ar_add_complete_missing_channel(self):
        mdl = ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode=self.EXECODE, ActionType=Execode.AR_ADD,
            Timestamp=now_utc_aware(), Data={
                AutoReplyModuleModel.Keyword.key: {
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                },
                AutoReplyModuleModel.Responses.key: [{
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                }],
                AutoReplyModuleModel.Pinned.key: False,
                AutoReplyModuleModel.Private.key: False,
                AutoReplyModuleModel.CooldownSec.key: 0,
                AutoReplyModuleModel.TagIds.key: []
            }
        )

        with self.assertRaises(ExecodeCollationError) as ex:
            ExecodeCompletor.complete_execode(mdl, {param.AutoReply.CHANNEL_TOKEN: "U12345"})

        self.assertEqual(ex.exception.err_code, ExecodeCollationFailedReason.MISSING_KEY)

        self.assertIsNone(ChannelManager.find_one())
        self.assertEqual(
            AutoReplyModuleManager.count({
                AutoReplyModuleModel.Keyword.key: {
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                },
                AutoReplyModuleModel.Responses.key: [{
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                }],
                AutoReplyModuleModel.Pinned.key: False,
                AutoReplyModuleModel.Private.key: False,
                AutoReplyModuleModel.CooldownSec.key: 0,
                AutoReplyModuleModel.TagIds.key: []
            }),
            0
        )

    def test_ar_add_complete_missing_token(self):
        mdl = ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode=self.EXECODE, ActionType=Execode.AR_ADD,
            Timestamp=now_utc_aware(), Data={
                AutoReplyModuleModel.Keyword.key: {
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                },
                AutoReplyModuleModel.Responses.key: [{
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                }],
                AutoReplyModuleModel.Pinned.key: False,
                AutoReplyModuleModel.Private.key: False,
                AutoReplyModuleModel.CooldownSec.key: 0,
                AutoReplyModuleModel.TagIds.key: []
            }
        )

        with self.assertRaises(ExecodeCollationError) as ex:
            ExecodeCompletor.complete_execode(mdl, {param.AutoReply.PLATFORM: "1"})

        self.assertEqual(ex.exception.err_code, ExecodeCollationFailedReason.MISSING_KEY)

        self.assertIsNone(ChannelManager.find_one())
        self.assertEqual(
            AutoReplyModuleManager.count({
                AutoReplyModuleModel.Keyword.key: {
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                },
                AutoReplyModuleModel.Responses.key: [{
                    AutoReplyContentModel.Content.key: "KEYWORD",
                    AutoReplyContentModel.ContentType.key: 0
                }],
                AutoReplyModuleModel.Pinned.key: False,
                AutoReplyModuleModel.Private.key: False,
                AutoReplyModuleModel.CooldownSec.key: 0,
                AutoReplyModuleModel.TagIds.key: []
            }),
            0
        )

    def test_reg_channel(self):
        mdl = ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode=self.EXECODE, ActionType=Execode.REGISTER_CHANNEL,
            Timestamp=now_utc_aware(), Data={}
        )

        outcome = ExecodeCompletor.complete_execode(mdl, {param.Execode.CHANNEL_TOKEN: "C12345",
                                                          param.Execode.PLATFORM: "1"})
        self.assertEqual(outcome, ExecodeCompletionOutcome.O_OK)

        self.assertEqual(
            ChannelManager.count({
                ChannelModel.Platform.key: 1,
                ChannelModel.Token.key: "C12345"
            }),
            1
        )

    def test_reg_channel_missing_token(self):
        mdl = ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode=self.EXECODE, ActionType=Execode.REGISTER_CHANNEL,
            Timestamp=now_utc_aware(), Data={}
        )

        with self.assertRaises(ExecodeCollationError) as ex:
            ExecodeCompletor.complete_execode(mdl, {param.Execode.PLATFORM: "1"})

        self.assertEqual(ex.exception.err_code, ExecodeCollationFailedReason.MISSING_KEY)

        self.assertEqual(
            ChannelManager.count({
                ChannelModel.Platform.key: 1
            }),
            0
        )

    def test_reg_channel_missing_platform(self):
        mdl = ExecodeEntryModel(
            CreatorOid=self.CREATOR_OID, Execode=self.EXECODE, ActionType=Execode.REGISTER_CHANNEL,
            Timestamp=now_utc_aware(), Data={}
        )

        with self.assertRaises(ExecodeCollationError) as ex:
            ExecodeCompletor.complete_execode(mdl, {param.Execode.CHANNEL_TOKEN: "C12345"})

        self.assertEqual(ex.exception.err_code, ExecodeCollationFailedReason.MISSING_KEY)

        self.assertEqual(
            ChannelManager.count({
                ChannelModel.Token.key: "C12345"
            }),
            0
        )

    def test_integrate_user_data(self):
        uid_1 = RootUserManager.register_onplat(Platform.LINE, "U12345").model.id
        uid_2 = RootUserManager.register_onplat(Platform.LINE, "U67890").model.id
        mdl = ExecodeEntryModel(
            CreatorOid=uid_2, Execode=self.EXECODE, ActionType=Execode.INTEGRATE_USER_DATA,
            Timestamp=now_utc_aware(), Data={}
        )

        outcome = ExecodeCompletor.complete_execode(mdl, {param.Execode.USER_OID: str(uid_1)})
        self.assertEqual(outcome, ExecodeCompletionOutcome.O_OK)

        self.assertEqual(RootUserManager.count({OID_KEY: uid_1}), 1)
        self.assertEqual(RootUserManager.count({OID_KEY: uid_2}), 0)

    def test_integrate_user_data_same_src_dst(self):
        uid_1 = RootUserManager.register_onplat(Platform.LINE, "U12345").model.id
        uid_2 = RootUserManager.register_onplat(Platform.LINE, "U67890").model.id
        mdl = ExecodeEntryModel(
            CreatorOid=uid_1, Execode=self.EXECODE, ActionType=Execode.INTEGRATE_USER_DATA,
            Timestamp=now_utc_aware(), Data={}
        )

        outcome = ExecodeCompletor.complete_execode(mdl, {param.Execode.USER_OID: str(uid_1)})
        self.assertEqual(outcome, ExecodeCompletionOutcome.X_IDT_SOURCE_EQ_TARGET)

        self.assertEqual(RootUserManager.count({OID_KEY: uid_1}), 1)
        self.assertEqual(RootUserManager.count({OID_KEY: uid_2}), 1)

    def test_integrate_user_data_src_not_found(self):
        uid_1 = ObjectId()
        uid_2 = RootUserManager.register_onplat(Platform.LINE, "U67890").model.id
        mdl = ExecodeEntryModel(
            CreatorOid=uid_1, Execode=self.EXECODE, ActionType=Execode.INTEGRATE_USER_DATA,
            Timestamp=now_utc_aware(), Data={}
        )

        outcome = ExecodeCompletor.complete_execode(mdl, {param.Execode.USER_OID: str(uid_2)})
        self.assertEqual(outcome, ExecodeCompletionOutcome.X_IDT_SOURCE_NOT_FOUND)

        self.assertEqual(RootUserManager.count({OID_KEY: uid_1}), 0)
        self.assertEqual(RootUserManager.count({OID_KEY: uid_2}), 1)

    def test_integrate_user_data_dst_not_found(self):
        uid_1 = RootUserManager.register_onplat(Platform.LINE, "U12345").model.id
        uid_2 = ObjectId()
        mdl = ExecodeEntryModel(
            CreatorOid=uid_1, Execode=self.EXECODE, ActionType=Execode.INTEGRATE_USER_DATA,
            Timestamp=now_utc_aware(), Data={}
        )

        outcome = ExecodeCompletor.complete_execode(mdl, {param.Execode.USER_OID: str(uid_2)})
        self.assertEqual(outcome, ExecodeCompletionOutcome.X_IDT_TARGET_NOT_FOUND)

        self.assertEqual(RootUserManager.count({OID_KEY: uid_1}), 1)
        self.assertEqual(RootUserManager.count({OID_KEY: uid_2}), 0)
