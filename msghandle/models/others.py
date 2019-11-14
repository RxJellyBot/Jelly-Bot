from dataclasses import dataclass
from typing import Optional

from flags import ImageContentType


@dataclass
class ImageContent:
    content: str
    content_type: ImageContentType
    comment: Optional[str] = None

    def __repr__(self):
        if self.content_type == ImageContentType.BASE64:
            return f"(Base64 Image), Comment={self.comment}"
        elif self.content_type == ImageContentType.URL:
            return f"Image at {self.content}, Comment={self.comment}"
        else:
            return super().__repr__()
