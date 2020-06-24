from extutils.line_sticker import LineStickerManager
from tests.base import TestCase

__all__ = ["TestLineStickerUtils"]


class TestLineStickerUtils(TestCase):
    def test_sticker_exists(self):
        self.assertTrue(LineStickerManager.is_sticker_exists("16663260"))
        self.assertTrue(LineStickerManager.is_sticker_exists(16663260))
        self.assertFalse(LineStickerManager.is_sticker_exists("88"))
        self.assertFalse(LineStickerManager.is_sticker_exists(88))
        self.assertFalse(LineStickerManager.is_sticker_exists(True))
