from abc import ABC
from typing import Optional


class ImgurResponse(ABC):
    def __init__(self, response: dict):
        self._dict = response

    @property
    def success(self) -> bool:
        return self._dict["success"]

    @property
    def status(self) -> int:
        return self._dict["status"]


class ImgurUploadResponse(ImgurResponse):
    def __init__(self, response: dict):
        super().__init__(response)

    @property
    def link(self) -> Optional[str]:
        if self.success:
            return self._dict["data"]["link"]
        else:
            return None
