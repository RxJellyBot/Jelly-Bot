"""
Imgur API response wrappers.
"""
from abc import ABC
from typing import Optional


class ImgurResponse(ABC):
    """
    Base response wrapper for imgur API.
    """

    def __init__(self, response: dict):
        self._dict = response

    @property
    def success(self) -> bool:
        """
        Check if the API request is successive.

        :return: if the API request is successive
        """
        return self._dict["success"]

    @property
    def status(self) -> int:
        """
        Get the status code of the API request.

        :return: status code of the APi request.
        """
        return self._dict["status"]


class ImgurUploadResponse(ImgurResponse):
    """
    Image upload response wrapper for imgur API.
    """

    @property
    def delete_hash(self) -> Optional[str]:
        """
        Get the delete hash of the uploaded image.

        :return: delete hash of the uploaded image
        """
        if self.success:
            return self._dict["data"]["deletehash"]

        return None

    @property
    def link(self) -> Optional[str]:
        """
        Get the link of the uploaded image

        :return: link of the uploaded image
        """
        if self.success:
            return self._dict["data"]["link"]

        return None
