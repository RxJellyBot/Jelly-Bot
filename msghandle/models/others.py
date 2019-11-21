from dataclasses import dataclass
from typing import Optional, Union

from flags import ImageContentType


@dataclass
class BaseContent:
    def __str__(self):
        return self.__repr__()


@dataclass
class ImageContent(BaseContent):
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


@dataclass
class LineStickerContent(BaseContent):
    package_id: Union[int, str]
    sticker_id: Union[int, str]

    def __repr__(self):
        return f"Package#{self.package_id} / Sticker#{self.sticker_id}"
