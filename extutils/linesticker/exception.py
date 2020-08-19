"""Exceptions that could possibly being raised when using LINE sticker utils."""
from typing import Union

__all__ = ("MetadataNotFoundError",)


class MetadataNotFoundError(Exception):
    """Raised if the metadata of a sticker set not found."""

    def __init__(self, package_id: Union[str, int]):
        super().__init__(f"Sticker metadata not found. Sticker Pack ID: {package_id}")
