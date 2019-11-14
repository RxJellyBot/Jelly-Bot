from dataclasses import dataclass
from typing import Optional

from flags import ImageContentType


@dataclass
class ImageContent:
    content: str
    content_type: ImageContentType
    comment: Optional[str] = None
