from extutils.line_sticker import LineStickerUtils
from tests.base import TestCase

__all__ = ["TestLineStickerUtils"]


class TestLineStickerUtils(TestCase):
    def test_sticker_exists(self):
        self.assertTrue(LineStickerUtils.is_sticker_exists("16663260"))
        self.assertTrue(LineStickerUtils.is_sticker_exists(16663260))
        self.assertFalse(LineStickerUtils.is_sticker_exists("88"))
        self.assertFalse(LineStickerUtils.is_sticker_exists(88))
        self.assertFalse(LineStickerUtils.is_sticker_exists(True))
