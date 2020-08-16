"""Module containing the flags related to LINE sticker utilities."""
from django.utils.translation import gettext_lazy as _

from extutils.flags import FlagSingleEnum

__all__ = ("LineStickerType", "LineStickerLanguage",)


class LineStickerType(FlagSingleEnum):
    """A :class:`FlagSingleEnum` indicating the type of the LINE sticker."""

    @classmethod
    def default(cls):
        return LineStickerType.STATIC

    ANIMATED = 0, _("Animated Sticker")
    SOUND = 1, _("Sticker with Sounds")
    STATIC = 2, _("Static Sticker")

    def to_extension(self):
        """
        Get the file extenstion of this :class:`LineStickerType`.

        :return: corresponding file extenstion
        """
        if self == LineStickerType.ANIMATED:
            return "gif"

        if self in (LineStickerType.SOUND, LineStickerType.STATIC):
            return "png"

        raise ValueError(f"No corresponding extension for {self}")


class LineStickerLanguage(FlagSingleEnum):
    """
    Currently known available languages for a sticker set.

    Will be used in LINE sticker metadata for localized object.
    """

    EN = 0, "en"  # English
    ES = 1, "es"  # Espanol
    IN = 2, "in"  # Indonesia
    JP = 3, "ja"  # Japan
    KR = 4, "ko"  # Korea
    TH = 5, "th"  # Thailand
    CHS = 6, "zh_CN"  # Simplified Chinese (China)
    CHT = 7, "zh_TW"  # Traditional Chinese (Taiwan)

    @classmethod
    def default(cls):
        """
        Get the default language code based on the current Django translation language.

        If there are any errors during the import of django, returns :class:`LineStickerLanguage.CHT`.

        :return: default sticker language
        """
        try:
            # On-demand import
            from django.utils.translation import get_language  # pylint: disable=import-outside-toplevel

            if get_language() == "en-us":
                return LineStickerLanguage.EN

            if get_language() == "zh-tw":
                return LineStickerLanguage.CHT
        except Exception:
            pass

        return LineStickerLanguage.CHT
