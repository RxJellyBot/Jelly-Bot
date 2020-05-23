from dataclasses import dataclass
from typing import Optional

from models import Model
from ._base import ModelResult


@dataclass
class AutoReplyModuleAddResult(ModelResult):
    exception: Optional[Exception] = None
    model: Optional[Model] = None


@dataclass
class AutoReplyModuleTagGetResult(ModelResult):
    pass
