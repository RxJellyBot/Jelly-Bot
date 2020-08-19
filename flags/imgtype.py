"""Module for image content type flags."""
from extutils.flags import FlagSingleEnum


class ImageContentType(FlagSingleEnum):
    """Supported types of image content."""

    URL = 0, "url"
    BASE64 = 1, "base64"
