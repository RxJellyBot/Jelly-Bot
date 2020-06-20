from rxtoolbox.flags import FlagSingleEnum


class ImageContentType(FlagSingleEnum):
    @classmethod
    def default(cls):
        return ImageContentType.UNKNOWN

    URL = 0, "URL"
    BASE64 = 1, "base64"
