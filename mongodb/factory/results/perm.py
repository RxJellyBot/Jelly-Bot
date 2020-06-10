from dataclasses import dataclass
from typing import Optional

from models import ChannelProfileModel

from ._base import ModelResult


@dataclass
class GetPermissionProfileResult(ModelResult):
    model: Optional[ChannelProfileModel] = None


@dataclass
class CreateProfileResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[ChannelProfileModel] = None
