"""Various managers controlling different collections."""
from typing import List, Type

from .factory import MONGO_CLIENT, new_mongo_session
from .rpdata import PendingRepairDataManager
from .channel import ChannelManager, ChannelCollectionManager
from .prof_main import ProfileManager
from .ar_conn import AutoReplyManager
from .user import RootUserManager
from .stats import APIStatisticsManager, MessageRecordStatisticsManager, BotFeatureUsageDataManager
from .execode import ExecodeManager
from .exctnt import ExtraContentManager
from .shorturl import ShortUrlDataManager
from .timer import TimerManager
from .rmc import RemoteControlManager

from ._base import BaseCollection
from ._dbctrl import SINGLE_DB_NAME, is_test_db, get_single_db_name

from .mixin import GenerateTokenMixin, ControlExtensionMixin


def get_collection_subclasses() -> List[Type[BaseCollection]]:
    """
    Get all classes that inherit ``BaseCollection``.

    :return: list of classes that inherit `BaseCollection`
    """
    return [cls for cls in BaseCollection.__subclasses__() if cls.__module__.split(".")[:2] == ["mongodb", "factory"]]
