from dataclasses import dataclass
from typing import Optional

from models import Model

from ._base import ModelResult


@dataclass
class GetPermissionProfileResult(ModelResult):
    model: Optional[Model] = None


@dataclass
class CreateProfileResult(ModelResult):
    pass
