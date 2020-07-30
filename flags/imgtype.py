from extutils.flags import FlagSingleEnum


class ImageContentType(FlagSingleEnum):
    @classmethod
    def default(cls):
        return ImageContentType.UNKNOWN

    URL = 0, "url"
    BASE64 = 1, "base64"
