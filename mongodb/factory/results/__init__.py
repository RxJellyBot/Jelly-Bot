from ._outcome import WriteOutcome, GetOutcome, OperationOutcome, UpdateOutcome
from ._base import BaseResult, ModelResult

from .user import (
    OnSiteUserRegistrationResult, OnPlatformUserRegistrationResult,
    RootUserRegistrationResult, RootUserUpdateResult, GetRootUserDataResult
)
from .ar import AutoReplyModuleAddResult, AutoReplyModuleTagGetResult
from .channel import (
    ChannelRegistrationResult, ChannelGetResult, ChannelChangeNameResult, ChannelCollectionRegistrationResult
)
from .statistics import RecordAPIStatisticsResult
from .execode import EnqueueExecodeResult, CompleteExecodeResult, GetExecodeEntryResult
from .perm import GetPermissionProfileResult, CreateProfileResult
from .exctnt import RecordExtraContentResult
from .shorturl import UrlShortenResult
