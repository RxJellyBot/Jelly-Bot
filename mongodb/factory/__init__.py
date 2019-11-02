from .factory import MONGO_CLIENT
# noinspection PyPep8Naming
from .rpdata import _inst as PendingRepairDataManager
# noinspection PyPep8Naming
from .channel import _inst as ChannelManager, _inst2 as ChannelCollectionManager
# noinspection PyPep8Naming
from .prof import _inst as ProfileManager
# noinspection PyPep8Naming
from .ar_ctnt import _inst as AutoReplyContentManager
# noinspection PyPep8Naming
from .ar_conn import _inst as AutoReplyManager
# noinspection PyPep8Naming
from .user import _inst as RootUserManager
# noinspection PyPep8Naming
from .stats import _inst as APIStatisticsManager, _inst2 as MessageRecordStatisticsManager
# noinspection PyPep8Naming
from .tkact import _inst as TokenActionManager
# noinspection PyPep8Naming
from .exctnt import _inst as ExtraContentManager
from ._base import BaseCollection


def get_collection_subclasses():
    return BaseCollection.__subclasses__()


def is_base_collection(o: object):
    return isinstance(o, BaseCollection)
