from dataclasses import dataclass
from typing import Optional

from models import ChannelModel, ChannelCollectionModel
from ._base import ModelResult


@dataclass
class ChannelRegistrationResult(ModelResult):
    model: ChannelModel


@dataclass
class ChannelGetResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[ChannelModel] = None


@dataclass
class ChannelChangeNameResult(ModelResult):
    model: ChannelModel


@dataclass
class ChannelCollectionRegistrationResult(ModelResult):
    model: ChannelCollectionModel
