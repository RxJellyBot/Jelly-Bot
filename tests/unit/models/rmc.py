from datetime import datetime
from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from extutils.dt import now_utc_aware
from extutils.locales import LocaleInfo
from flags import Platform
from models import Model, RemoteControlEntryModel, ChannelModel, ChannelConfigModel
from mongodb.factory import ChannelManager

from tests.base import TestModel, TestModelMixin

__all__ = ["TestRemoteControlEntryModel"]


class TestRemoteControlEntryModel(TestModel.TestClass, TestModelMixin):
    USER_OID = ObjectId()
    SRC_CID = ObjectId()
    TGT_CID = ObjectId()
    EXPIRY = now_utc_aware()

    PROF_OID = ObjectId()

    @staticmethod
    def obj_to_clear():
        return [ChannelManager]

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return RemoteControlEntryModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("uid", "UserOid"): TestRemoteControlEntryModel.USER_OID,
            ("src", "SourceChannelOid"): TestRemoteControlEntryModel.SRC_CID,
            ("dst", "TargetChannelOid"): TestRemoteControlEntryModel.TGT_CID,
            ("exp", "ExpiryUtc"): TestRemoteControlEntryModel.EXPIRY,
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("loc", "LocaleCode"): ("Asia/Taipei", "US/Central")
        }

    def test_expiry(self):
        loc = "Asia/Taipei"
        exp = datetime(2020, 5, 15)

        exp_aware = exp.replace(hour=8, tzinfo=LocaleInfo.get_tzinfo(loc))

        mdl = self.get_constructed_model(exp=exp, loc=loc)

        self.assertEqual(mdl.expiry, exp_aware)
        self.assertEqual(mdl.expiry_str, "2020-05-15 08:00:00 (UTC+0800)")

    @classmethod
    def prepare_channel_data(cls):
        c_model = ChannelModel(
            Id=cls.TGT_CID, Platform=Platform.LINE, Token="ABC",
            Config=ChannelConfigModel.generate_default(DefaultProfileOid=cls.PROF_OID)
        )
        ChannelManager.insert_one_model(c_model)

        return c_model

    def test_target_channel(self):
        expected_channel_mdl = self.prepare_channel_data()
        mdl = self.get_constructed_model(dst=expected_channel_mdl.id)

        self.assertModelEqual(mdl.target_channel, expected_channel_mdl, ignore_oid=False)
