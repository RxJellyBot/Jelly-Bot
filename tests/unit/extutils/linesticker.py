from extutils.linesticker import LineStickerUtils
from tests.base import TestCase

__all__ = ["TestLineStickerUtils"]


class TestLineStickerUtils(TestCase):
    def test_sticker_exists(self):
        self.assertTrue(LineStickerUtils.is_sticker_exists("16663260"))
        self.assertTrue(LineStickerUtils.is_sticker_exists(16663260))
        self.assertFalse(LineStickerUtils.is_sticker_exists("88"))
        self.assertFalse(LineStickerUtils.is_sticker_exists(88))
        self.assertFalse(LineStickerUtils.is_sticker_exists(True))

    def test_extract_pack_url(self):
        data = [
            ("From phone", "https://line.me/S/sticker/12542626/?lang=en&ref=gnsh_stickerDetail", 12542626),
            ("From phone (http)", "http://line.me/S/sticker/12542626/?lang=en&ref=gnsh_stickerDetail", 12542626),
            ("From PC", "https://store.line.me/stickershop/product/17811/?ref=Desktop", 17811),
            ("From PC (http)", "http://store.line.me/stickershop/product/17811/?ref=Desktop", 17811),
            ("Unavailable", "https://line.me/S/sticker/0/?lang=en&ref=gnsh_stickerDetail", 0),
            ("Unparsable", "https://google.com", None)
        ]

        for name, url, expected_return in data:
            with self.subTest(name):
                if expected_return:
                    self.assertEqual(LineStickerUtils.get_pack_meta_from_url(url).pack_id, expected_return)
                else:
                    self.assertIsNone(LineStickerUtils.get_pack_meta_from_url(url))
