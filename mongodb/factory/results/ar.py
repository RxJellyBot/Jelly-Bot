from dataclasses import dataclass
from typing import Optional

from models import AutoReplyModuleModel, AutoReplyModuleTagModel
from ._base import ModelResult


@dataclass
class AutoReplyModuleAddResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[AutoReplyModuleModel] = None


@dataclass
class AutoReplyModuleTagGetResult(ModelResult):
    model: AutoReplyModuleTagModel
