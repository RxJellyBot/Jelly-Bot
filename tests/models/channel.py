from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from flags import Platform
from models import Model, ChannelConfigModel, ChannelModel, ChannelCollectionModel
from JellyBot.systemconfig import ChannelConfig

from ._test_base import TestModel

__all__ = ["TestChannelConfigModel", "TestChannelCollectionModel", "TestChannelModel"]


# region ChannelConfigModel

class TestChannelConfigModel(TestModel.TestClass):
    DEFAULT_POID = ObjectId()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return ChannelConfigModel

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("v-m", "VotePromoMod"): (ChannelConfig.VotesToPromoteMod, 100),
            ("v-a", "VotePromoAdmin"): (ChannelConfig.VotesToPromoteAdmin, 100),
            ("e-ar", "EnableAutoReply"): (True, False),
            ("e-tmr", "EnableTimer"): (True, False),
            ("e-calc", "EnableCalculator"): (True, False),
            ("e-bot", "EnableBotCommand"): (True, False),
            ("prv", "InfoPrivate"): (False, True),
            ("d-prof", "DefaultProfileOid"): (None, cls.DEFAULT_POID),
            ("d-name", "DefaultName"): (None, "XXX")
        }


# endregion


# region ChannelModel

class TestChannelModel(TestModel.TestClass):
    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return ChannelModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("p", "Platform"): Platform.LINE,
            ("t", "Token"): "XYZ"
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("n", "Name"): ({}, {"DEF": "NAME"}),
            ("c", "Config"): (ChannelConfigModel(), ChannelConfigModel(DefaultName="DN")),
            ("acc", "BotAccessible"): (True, False)
        }

    def test_get_channel_name(self):
        mdl = self.get_constructed_model(manual_default=True)
        self.assertEquals(mdl.get_channel_name("ABC"), "DN")
        self.assertEquals(mdl.get_channel_name("DEF"), "NAME")

        mdl = self.get_constructed_model(manual_default=False)
        self.assertEquals(mdl.get_channel_name("ABC"), "XYZ")
        self.assertEquals(mdl.get_channel_name("DEF"), "XYZ")


# endregion


# region ChannelCollectionModel

class TestChannelCollectionModel(TestModel.TestClass):
    CHILD_COID = [ObjectId(), ObjectId(), ObjectId()]

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return ChannelCollectionModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("dn", "DefaultName"): "Default",
            ("p", "Platform"): Platform.DISCORD,
            ("t", "Token"): "Token"
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("n", "Name"): ({}, {"ABC": "NM"}),
            ("acc", "BotAccessible"): (True, False),
            ("ch", "ChildChannelOids"): ([], TestChannelCollectionModel.CHILD_COID)
        }

# endregion
