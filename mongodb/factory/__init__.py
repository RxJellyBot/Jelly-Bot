from .factory import MONGO_CLIENT
# noinspection PyPep8Naming
from .rpdata import _inst as PendingRepairDataManager
# noinspection PyPep8Naming
from .channel import _inst as ChannelManager, _inst2 as ChannelCollectionManager
# noinspection PyPep8Naming
from .prof import _inst as ProfileManager
# noinspection PyPep8Naming
from .ar_conn import _inst as AutoReplyManager
# noinspection PyPep8Naming
from .user import _inst as RootUserManager
# noinspection PyPep8Naming
from .stats import (
    _inst as APIStatisticsManager,
    _inst2 as MessageRecordStatisticsManager,
    _inst3 as BotFeatureUsageDataManager
)
# noinspection PyPep8Naming
from .execode import _inst as ExecodeManager
# noinspection PyPep8Naming
from .exctnt import _inst as ExtraContentManager
# noinspection PyPep8Naming
from .shorturl import _inst as ShortUrlDataManager
# noinspection PyPep8Naming
from .timer import _inst as TimerManager
# noinspection PyPep8Naming
from .rmc import _inst as RemoteControlManager

from ._base import BaseCollection, SINGLE_DB_NAME, is_test_db, get_single_db_name


def get_collection_subclasses():
    return BaseCollection.__subclasses__()


def is_base_collection(o: object):
    return isinstance(o, BaseCollection)
