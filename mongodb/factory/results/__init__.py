from ._outcome import WriteOutcome, GetOutcome, OperationOutcome, UpdateOutcome
from ._base import BaseResult
from .user import (
    OnSiteUserRegistrationResult, OnPlatformUserRegistrationResult,
    RootUserRegistrationResult, GetRootUserDataApiResult, RootUserUpdateResult,
    GetRootUserDataResult
)
from .ar import (
    AutoReplyContentAddResult, AutoReplyModuleAddResult,
    AutoReplyContentGetResult, AutoReplyModuleTagGetResult
)
from .channel import ChannelRegistrationResult, ChannelGetResult, ChannelChangeNameResult
from .statistics import RecordAPIStatisticsResult, MessageRecordResult
from .tkact import EnqueueTokenActionResult, CompleteTokenActionResult
from .perm import GetPermissionProfileResult, CreatePermissionProfileResult
from .exctnt import RecordExtraContentResult
