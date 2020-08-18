import copy
import os
from tempfile import TemporaryDirectory
from zipfile import is_zipfile, ZipFile

from extutils.line_sticker import LineStickerUtils, LineStickerMetadata, MetadataNotFoundError, LineStickerLanguage
from tests.base import TestCase

__all__ = ["TestLineStickerUtils", "TestLineStickerMetadata"]


class TestLineStickerUtils(TestCase):
    """
    .. note::

        To ensure that the downloaded files are deleted,
        output path should be given and a wrapper temp directory should be used as default.
    """

    @staticmethod
    def obj_to_clear():
        return [LineStickerUtils]

    def test_sticker_exists(self):
        self.assertTrue(LineStickerUtils.is_sticker_exists("16663260"))
        self.assertTrue(LineStickerUtils.is_sticker_exists(16663260))
        self.assertFalse(LineStickerUtils.is_sticker_exists("88"))
        self.assertFalse(LineStickerUtils.is_sticker_exists(88))
        self.assertFalse(LineStickerUtils.is_sticker_exists(True))

    def test_download_animated_get_integer_id(self):
        result = LineStickerUtils.download_apng_as_gif(15769, 248521690)

        self.assertEqual(result.sticker_id, 248521690)
        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.conversion_result.succeed)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_animated(15769, 248521690) as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

        with LineStickerUtils.get_downloaded_apng_frames(15769, 248521690) as f:
            self.assertTrue(is_zipfile(f))
            self.assertGreaterEqual(len(ZipFile(f).namelist()), 0)

    def test_download_animated(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path)

            self.assertEqual(result.sticker_id, 248521690)
            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.conversion_result.succeed)
            self.assertTrue(result.conversion_result.frame_zipping.success)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

            self.assertTrue(is_zipfile(out_path_frames))
            self.assertGreaterEqual(len(ZipFile(out_path_frames).namelist()), 0)

    def test_download_animated_2(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            result = LineStickerUtils.download_apng_as_gif("15563", "238476641", out_path)

            self.assertEqual(result.sticker_id, 238476641)
            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.conversion_result.succeed)
            self.assertTrue(result.conversion_result.frame_zipping.success)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

            self.assertTrue(is_zipfile(out_path_frames))
            self.assertGreaterEqual(len(ZipFile(out_path_frames).namelist()), 0)

    def test_download_animated_no_frames(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path, with_frames=False)

            self.assertEqual(result.sticker_id, 248521690)
            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.conversion_result.succeed)
            self.assertFalse(result.conversion_result.frame_zipping.success)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))
            self.assertFalse(os.path.exists(out_path_frames))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_download_animated_already_downloaded_all(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path)

            self.assertEqual(result.sticker_id, 248521690)
            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.conversion_result.succeed)
            self.assertTrue(result.conversion_result.frame_zipping.success)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path)

            self.assertEqual(result.sticker_id, 248521690)
            self.assertTrue(result.available)
            self.assertTrue(result.already_exists)
            self.assertIsNone(result.conversion_result)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

            self.assertTrue(is_zipfile(out_path_frames))
            self.assertGreaterEqual(len(ZipFile(out_path_frames).namelist()), 0)

    def test_download_animated_already_downloaded_no_frames(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path, with_frames=False)

            self.assertEqual(result.sticker_id, 248521690)
            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.conversion_result.succeed)
            self.assertFalse(result.conversion_result.frame_zipping.success)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path)

            self.assertEqual(result.sticker_id, 248521690)
            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.conversion_result.succeed)
            self.assertTrue(result.conversion_result.frame_zipping.success)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

            self.assertTrue(is_zipfile(out_path_frames))
            self.assertGreaterEqual(len(ZipFile(out_path_frames).namelist()), 0)

    def test_download_animated_output_path_not_given(self):
        result = LineStickerUtils.download_apng_as_gif("15769", "248521690")

        self.assertEqual(result.sticker_id, 248521690)
        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.conversion_result.succeed)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_animated("15769", "248521690") as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_download_animated_already_downloaded_output_path_not_given(self):
        result = LineStickerUtils.download_apng_as_gif("15769", "248521690")

        self.assertEqual(result.sticker_id, 248521690)
        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.conversion_result.succeed)
        self.assertTrue(result.succeed)

        result = LineStickerUtils.download_apng_as_gif("15769", "248521690")

        self.assertEqual(result.sticker_id, 248521690)
        self.assertTrue(result.available)
        self.assertTrue(result.already_exists)
        self.assertIsNone(result.conversion_result)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_animated("15769", "248521690") as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_download_animated_not_exists(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")

            result = LineStickerUtils.download_apng_as_gif("1", "1", out_path)

            self.assertEqual(result.sticker_id, 1)
            self.assertFalse(result.available)
            self.assertFalse(result.already_exists)
            self.assertIsNone(result.conversion_result)
            self.assertFalse(result.succeed)
            self.assertFalse(os.path.exists(out_path))

    def test_download_animated_not_exists_dummy_exists(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_dummy = os.path.join(temp_dir, "1.gif")

            with open(out_path_dummy, "w") as _:
                pass

            self.assertTrue(os.path.exists(out_path_dummy))

            result = LineStickerUtils.download_apng_as_gif("1", "1", out_path)

            self.assertEqual(result.sticker_id, 1)
            self.assertFalse(result.available)
            self.assertFalse(result.already_exists)
            self.assertIsNone(result.conversion_result)
            self.assertFalse(result.succeed)
            self.assertFalse(os.path.exists(out_path))

    def test_get_downloaded_animated(self):
        result = LineStickerUtils.download_apng_as_gif("15769", "248521690")

        self.assertEqual(result.sticker_id, 248521690)
        self.assertTrue(result.available)
        self.assertTrue(result.conversion_result.frame_zipping.success)
        self.assertTrue(result.conversion_result.succeed)

        with LineStickerUtils.get_downloaded_animated("15769", "248521690") as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_get_downloaded_animated_not_downloaded(self):
        with LineStickerUtils.get_downloaded_animated("15769", "248521690") as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_get_downloaded_animated_not_exists(self):
        self.assertIsNone(LineStickerUtils.get_downloaded_animated("1", "1"))

    def test_get_downloaded_animated_frames(self):
        result = LineStickerUtils.download_apng_as_gif("15769", "248521690")

        self.assertEqual(result.sticker_id, 248521690)
        self.assertTrue(result.available)
        self.assertTrue(result.conversion_result.succeed)
        self.assertTrue(result.conversion_result.frame_zipping.success)

        with LineStickerUtils.get_downloaded_apng_frames("15769", "248521690") as f:
            self.assertTrue(is_zipfile(f))
            self.assertGreaterEqual(len(ZipFile(f).namelist()), 0)

    def test_get_downloaded_animated_frames_not_downloaded(self):
        with LineStickerUtils.get_downloaded_apng_frames("15769", "248521690") as f:
            self.assertTrue(is_zipfile(f))
            self.assertGreaterEqual(len(ZipFile(f).namelist()), 0)

    def test_get_downloaded_animated_frames_not_exists(self):
        self.assertIsNone(LineStickerUtils.get_downloaded_apng_frames("1", "1"))

    def test_download_static_get_integer_id(self):
        result = LineStickerUtils.download_sticker(317509827)

        self.assertEqual(result.sticker_id, 317509827)
        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.downloaded)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_sticker(317509827) as f:
            self.assertTrue(f.read(8) == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")

    def test_download_static(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.png")

            result = LineStickerUtils.download_sticker("317509827", out_path)

            self.assertEqual(result.sticker_id, 317509827)
            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.downloaded)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(8) == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")

    def test_download_static_already_downloaded(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.png")

            result = LineStickerUtils.download_sticker("317509827", out_path)

            self.assertEqual(result.sticker_id, 317509827)
            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.downloaded)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            result = LineStickerUtils.download_sticker("317509827", out_path)

            self.assertEqual(result.sticker_id, 317509827)
            self.assertTrue(result.available)
            self.assertTrue(result.already_exists)
            self.assertFalse(result.downloaded)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(8) == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")

    def test_download_static_output_path_not_given(self):
        result = LineStickerUtils.download_sticker("317509827")

        self.assertEqual(result.sticker_id, 317509827)
        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.downloaded)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_sticker("317509827") as f:
            self.assertTrue(f.read(8) == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")

    def test_download_static_already_downloaded_output_path_not_given(self):
        result = LineStickerUtils.download_sticker("317509827")

        self.assertEqual(result.sticker_id, 317509827)
        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.downloaded)
        self.assertTrue(result.succeed)

        result = LineStickerUtils.download_sticker("317509827")

        self.assertEqual(result.sticker_id, 317509827)
        self.assertTrue(result.available)
        self.assertTrue(result.already_exists)
        self.assertFalse(result.downloaded)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_sticker("317509827") as f:
            self.assertTrue(f.read(8) == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")

    def test_download_static_not_exists(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.png")

            result = LineStickerUtils.download_sticker("87", out_path)

            self.assertEqual(result.sticker_id, 87)
            self.assertFalse(result.available)
            self.assertFalse(result.already_exists)
            self.assertFalse(result.downloaded)
            self.assertFalse(result.succeed)
            self.assertFalse(os.path.exists(out_path))

    def test_download_static_not_exists_dummy_exists(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.png")
            out_path_dummy = os.path.join(temp_dir, "87.png")

            with open(out_path_dummy, "w") as _:
                pass

            self.assertTrue(os.path.exists(out_path_dummy))

            result = LineStickerUtils.download_sticker("87", out_path)

            self.assertEqual(result.sticker_id, 87)
            self.assertFalse(result.available)
            self.assertFalse(result.already_exists)
            self.assertFalse(result.downloaded)
            self.assertFalse(result.succeed)
            self.assertFalse(os.path.exists(out_path))

    def test_get_downloaded_static(self):
        result = LineStickerUtils.download_sticker("317509827")

        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_sticker("317509827") as f:
            self.assertTrue(f.read(8) == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")

    def test_get_downloaded_static_not_downloaded(self):
        with LineStickerUtils.get_downloaded_sticker("317509827") as f:
            self.assertTrue(f.read(8) == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a")

    def test_get_downloaded_static_not_exists(self):
        self.assertIsNone(LineStickerUtils.get_downloaded_animated("1", "87"))

    def test_get_pack_meta(self):
        metadata = LineStickerUtils.get_pack_meta("11952172")

        self.assertEqual(metadata.pack_id, 11952172)
        self.assertFalse(metadata.is_animated_sticker)
        self.assertFalse(metadata.has_sound)
        self.assertEqual(metadata.sticker_ids, list(range(317509814, 317509854)))
        self.assertEqual(metadata.get_author(LineStickerLanguage.EN), "A-way")
        self.assertEqual(metadata.get_title(LineStickerLanguage.EN), "LV.14 Meow meow Monster")

    def test_get_pack_meta_int_id(self):
        metadata = LineStickerUtils.get_pack_meta(11952172)

        self.assertEqual(metadata.pack_id, 11952172)
        self.assertFalse(metadata.is_animated_sticker)
        self.assertFalse(metadata.has_sound)
        self.assertEqual(metadata.sticker_ids, list(range(317509814, 317509854)))
        self.assertEqual(metadata.get_author(LineStickerLanguage.EN), "A-way")
        self.assertEqual(metadata.get_title(LineStickerLanguage.EN), "LV.14 Meow meow Monster")

    def test_get_pack_meta_not_exists(self):
        with self.assertRaises(MetadataNotFoundError):
            LineStickerUtils.get_pack_meta("1")

    def test_download_pack_int_id(self):
        result = LineStickerUtils.download_sticker_pack(11952172)

        self.assertEqual(result.pack_meta.pack_id, 11952172)
        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.download_succeed)
        self.assertTrue(result.zip_succeed)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_sticker_pack(11952172) as f:
            self.assertTrue(f.read(4) == b"\x50\x4b\x03\x04")

        with ZipFile(LineStickerUtils.get_downloaded_sticker_pack(11952172)) as zip_file:
            name_list = zip_file.namelist()
            self.assertGreater(len(name_list), 0)
            self.assertTrue(all(f_name.endswith(".png") for f_name in name_list))

    def test_download_pack_static(self):
        result = LineStickerUtils.download_sticker_pack("11952172")

        self.assertEqual(result.pack_meta.pack_id, 11952172)
        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.download_succeed)
        self.assertTrue(result.zip_succeed)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_sticker_pack("11952172") as f:
            self.assertTrue(f.read(4) == b"\x50\x4b\x03\x04")

        with ZipFile(LineStickerUtils.get_downloaded_sticker_pack("11952172")) as zip_file:
            name_list = zip_file.namelist()
            self.assertGreater(len(name_list), 0)
            self.assertTrue(all(f_name.endswith(".png") for f_name in name_list))

    def test_download_pack_animated(self):
        result = LineStickerUtils.download_sticker_pack("15769")

        self.assertEqual(result.pack_meta.pack_id, 15769)
        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.download_succeed, result.missed_sticker_ids)
        self.assertTrue(result.zip_succeed, result.not_zipped_ids)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_sticker_pack("15769") as f:
            self.assertTrue(f.read(4) == b"\x50\x4b\x03\x04")

        with ZipFile(LineStickerUtils.get_downloaded_sticker_pack("15769")) as zip_file:
            name_list = zip_file.namelist()
            self.assertGreater(len(name_list), 0)
            self.assertTrue(all(f_name.endswith(".gif") for f_name in name_list), name_list)

    def test_download_pack_already_downloaded(self):
        result = LineStickerUtils.download_sticker_pack("11952172")

        self.assertTrue(result.succeed)

        result = LineStickerUtils.download_sticker_pack("11952172")

        self.assertEqual(result.pack_meta.pack_id, 11952172)
        self.assertTrue(result.available)
        self.assertTrue(result.already_exists)
        self.assertFalse(result.download_succeed)
        self.assertFalse(result.zip_succeed)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_sticker_pack("11952172") as f:
            self.assertTrue(f.read(4) == b"\x50\x4b\x03\x04")

        with ZipFile(LineStickerUtils.get_downloaded_sticker_pack("11952172")) as zip_file:
            name_list = zip_file.namelist()
            self.assertGreater(len(name_list), 0)
            self.assertTrue(all(f_name.endswith(".png") for f_name in name_list))

    def test_download_pack_not_exists(self):
        result = LineStickerUtils.download_sticker_pack("1")

        self.assertIsNone(result.pack_meta, 1)
        self.assertFalse(result.available)
        self.assertFalse(result.already_exists)
        self.assertFalse(result.download_succeed)
        self.assertFalse(result.zip_succeed)
        self.assertFalse(result.succeed)

    def test_get_downloaded_pack(self):
        result = LineStickerUtils.download_sticker_pack("11952172")

        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_sticker_pack("11952172") as f:
            self.assertTrue(f.read(4) == b"\x50\x4b\x03\x04")

    def test_get_downloaded_pack_not_downloaded(self):
        with LineStickerUtils.get_downloaded_sticker_pack("11952172") as f:
            self.assertTrue(f.read(4) == b"\x50\x4b\x03\x04")

    def test_get_downloaded_pack_not_exists(self):
        self.assertIsNone(LineStickerUtils.get_downloaded_sticker_pack("1"))


class TestLineStickerMetadata(TestCase):
    TEST_DICT = {
        "packageId": 11952172,
        "onSale": True,
        "validDays": 0,
        "title": {"en": "LV.14 Meow meow Monster", "zh_TW": "LV.14 野生喵喵怪 (附草泥馬)"},
        "author": {"en": "A-way", "zh_TW": "胸毛公寓"},
        "price": [
            {"country": "@@", "currency": "NLC", "symbol": "NLC", "price": 50.0},
            {"country": "ID", "currency": "IDR", "symbol": "Rp", "price": 12000.0},
            {"country": "JP", "currency": "JPY", "symbol": "￥", "price": 120.0},
            {"country": "TH", "currency": "THB", "symbol": "THB", "price": 30.0},
            {"country": "TW", "currency": "TWD", "symbol": "NT$", "price": 33.0},
            {"country": "US", "currency": "USD", "symbol": "$", "price": 0.99}
        ],
        "stickers": [
            {"id": 317509814, "width": 259, "height": 224},
            {"id": 317509815, "width": 259, "height": 224},
            {"id": 317509816, "width": 259, "height": 224},
            {"id": 317509817, "width": 259, "height": 224},
            {"id": 317509818, "width": 259, "height": 224},
            {"id": 317509819, "width": 259, "height": 224},
            {"id": 317509820, "width": 259, "height": 224},
            {"id": 317509821, "width": 259, "height": 224},
            {"id": 317509822, "width": 259, "height": 224},
            {"id": 317509823, "width": 259, "height": 224},
            {"id": 317509824, "width": 259, "height": 224},
            {"id": 317509825, "width": 259, "height": 224},
            {"id": 317509826, "width": 259, "height": 224},
            {"id": 317509827, "width": 259, "height": 224},
            {"id": 317509828, "width": 259, "height": 224},
            {"id": 317509829, "width": 259, "height": 224},
            {"id": 317509830, "width": 259, "height": 224},
            {"id": 317509831, "width": 259, "height": 224},
            {"id": 317509832, "width": 259, "height": 224},
            {"id": 317509833, "width": 259, "height": 224},
            {"id": 317509834, "width": 259, "height": 224},
            {"id": 317509835, "width": 259, "height": 224},
            {"id": 317509836, "width": 259, "height": 224},
            {"id": 317509837, "width": 259, "height": 224},
            {"id": 317509838, "width": 259, "height": 224},
            {"id": 317509839, "width": 259, "height": 224},
            {"id": 317509840, "width": 259, "height": 224},
            {"id": 317509841, "width": 259, "height": 224},
            {"id": 317509842, "width": 259, "height": 224},
            {"id": 317509843, "width": 259, "height": 224},
            {"id": 317509844, "width": 259, "height": 224},
            {"id": 317509845, "width": 259, "height": 224},
            {"id": 317509846, "width": 259, "height": 224},
            {"id": 317509847, "width": 259, "height": 224},
            {"id": 317509848, "width": 259, "height": 224},
            {"id": 317509849, "width": 259, "height": 224},
            {"id": 317509850, "width": 259, "height": 224},
            {"id": 317509851, "width": 259, "height": 224},
            {"id": 317509852, "width": 259, "height": 224},
            {"id": 317509853, "width": 259, "height": 224}
        ],
        "hasAnimation": False,
        "hasSound": False,
        "stickerResourceType": "STATIC"
    }

    def test_from_dict(self):
        metadata = LineStickerMetadata(self.TEST_DICT)

        self.assertEqual(metadata.pack_id, 11952172)
        self.assertFalse(metadata.is_animated_sticker)
        self.assertFalse(metadata.has_sound)
        self.assertEqual(metadata.sticker_ids, list(range(317509814, 317509854)))

    def test_get_localized(self):
        metadata = LineStickerMetadata(self.TEST_DICT)

        self.assertEqual(metadata.get_author(LineStickerLanguage.EN), "A-way")
        self.assertEqual(metadata.get_title(LineStickerLanguage.EN), "LV.14 Meow meow Monster")

    def test_get_localized_use_default(self):
        metadata = LineStickerMetadata(self.TEST_DICT)

        self.assertEqual(metadata.get_author(), "胸毛公寓")
        self.assertEqual(metadata.get_title(), "LV.14 野生喵喵怪 (附草泥馬)")

    def test_get_localized_fallback_default(self):
        metadata = LineStickerMetadata(self.TEST_DICT)

        self.assertEqual(metadata.get_author(LineStickerLanguage.JP), "胸毛公寓")
        self.assertEqual(metadata.get_title(LineStickerLanguage.JP), "LV.14 野生喵喵怪 (附草泥馬)")

    def test_get_localized_default_not_exists(self):
        test_dict = copy.deepcopy(self.TEST_DICT)
        del test_dict["author"]["zh_TW"]
        del test_dict["title"]["zh_TW"]

        metadata = LineStickerMetadata(test_dict)

        self.assertEqual(metadata.get_author(), "A-way")
        self.assertEqual(metadata.get_title(), "LV.14 Meow meow Monster")
