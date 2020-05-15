from datetime import datetime, timezone
from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from extutils.locales import LocaleInfo
from flags import Platform
from models import Model, RemoteControlEntryModel, ChannelModel
from mongodb.factory import ChannelManager

from ._test_base import TestModel

__all__ = ["TestRemoteControlEntryModel"]


class TestRemoteControlEntryModel(TestModel.TestClass):
    USER_OID = ObjectId()
    SRC_CID = ObjectId()
    TGT_CID = ObjectId()
    EXPIRY = datetime.utcnow().replace(tzinfo=timezone.utc)

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

        self.assertEquals(mdl.expiry, exp_aware)
        self.assertEquals(mdl.expiry_str, "2020-05-15 08:00:00 (UTC+0800)")

    @staticmethod
    def prepare_channel_data():
        c_model = ChannelModel(Platform=Platform.LINE, Token="ABC")
        ChannelManager.insert_one_model(c_model)

        return c_model

    def test_target_channel(self):
        expected_channel_mdl = self.prepare_channel_data()
        mdl = self.get_constructed_model(dst=expected_channel_mdl.id)

        self.assertEquals(mdl.target_channel, expected_channel_mdl)
