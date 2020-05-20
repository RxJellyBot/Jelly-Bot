from datetime import datetime, timezone
from typing import Dict, Tuple, Any, Type

from bson import ObjectId

from flags import APICommand, MessageType, BotFeature
from models import Model, APIStatisticModel, MessageRecordModel, BotFeatureUsageModel

from ._test_base import TestModel

__all__ = ["TestAPIStatisticModel"]


class TestAPIStatisticModel(TestModel.TestClass):
    DEFAULT_TIME = datetime.now().replace(tzinfo=timezone.utc)
    SENDER_OID = ObjectId()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return APIStatisticModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("t", "Timestamp"): TestAPIStatisticModel.DEFAULT_TIME,
            ("pi", "PathInfo"): "/ar/add",
            ("pf", "PathInfoFull"): "https://localhost:8000/ar/add"
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("a", "ApiAction"): (APICommand.UNKNOWN, APICommand.AR_ADD),
            ("p", "Parameter"): (None, {"A": "B"}),
            ("pp", "PathParameter"): (None, {"C": "D"}),
            ("r", "Response"): (None, {"E": "F"}),
            ("s", "Success"): (None, True)
        }

    @classmethod
    def get_optional(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("sd", "SenderOid"): TestAPIStatisticModel.SENDER_OID
        }


class TestMessageRecordModel(TestModel.TestClass):
    CHANNEL_OID = ObjectId()
    USER_OID = ObjectId()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return MessageRecordModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("ch", "ChannelOid"): TestMessageRecordModel.CHANNEL_OID,
            ("u", "UserRootOid"): TestMessageRecordModel.USER_OID,
            ("t", "MessageType"): MessageType.TEXT,
            ("ct", "MessageContent"): "ABCDE"
        }

    @classmethod
    def get_optional(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("pt", "ProcessTimeSecs"): 0.7
        }

    @classmethod
    def get_default(cls) -> Dict[Tuple[str, str], Tuple[Any, Any]]:
        return {
            ("ts", "Timestamp"): (datetime.min.replace(tzinfo=timezone.utc),
                                  datetime.now().replace(tzinfo=timezone.utc))
        }


class TestBotFeatureUsageModel(TestModel.TestClass):
    CHANNEL_OID = ObjectId()
    SENDER_OID = ObjectId()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        return BotFeatureUsageModel

    @classmethod
    def get_required(cls) -> Dict[Tuple[str, str], Any]:
        return {
            ("ft", "Feature"): BotFeature.IMG_IMGUR_UPLOAD,
            ("ch", "ChannelOid"): TestBotFeatureUsageModel.CHANNEL_OID,
            ("u", "SenderRootOid"): TestBotFeatureUsageModel.SENDER_OID
        }
