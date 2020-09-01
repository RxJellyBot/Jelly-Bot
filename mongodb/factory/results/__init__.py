"""Module for the result objects."""
from ._outcome import WriteOutcome, GetOutcome, OperationOutcome, UpdateOutcome
from ._base import BaseResult, ModelResult

from .user import (
    APIUserRegistrationResult, OnPlatformUserRegistrationResult,
    RootUserRegistrationResult, RootUserUpdateResult, GetRootUserDataResult
)
from .ar import AutoReplyModuleAddResult, AutoReplyModuleTagGetResult
from .channel import (
    ChannelRegistrationResult, ChannelGetResult, ChannelChangeNameResult, ChannelCollectionRegistrationResult
)
from .statistics import RecordAPIStatisticsResult
from .execode import EnqueueExecodeResult, CompleteExecodeResult, GetExecodeEntryResult
from .prof import GetPermissionProfileResult, CreateProfileResult, RegisterProfileResult, ArgumentParseResult
from .exctnt import RecordExtraContentResult
from .shorturl import UrlShortenResult
