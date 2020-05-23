from dataclasses import dataclass
from typing import Optional

from models import Model
from ._base import ModelResult


@dataclass
class ChannelRegistrationResult(ModelResult):
    pass


@dataclass
class ChannelGetResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[Model] = None


@dataclass
class ChannelChangeNameResult(ModelResult):
    pass


@dataclass
class ChannelCollectionRegistrationResult(ModelResult):
    pass
