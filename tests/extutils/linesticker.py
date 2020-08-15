import os
from tempfile import TemporaryDirectory
from zipfile import is_zipfile, ZipFile

from extutils.line_sticker import LineStickerUtils
from tests.base import TestCase

__all__ = ["TestLineStickerUtils"]


class TestLineStickerUtils(TestCase):
    @staticmethod
    def obj_to_clear():
        return [LineStickerUtils]

    def test_sticker_exists(self):
        self.assertTrue(LineStickerUtils.is_sticker_exists("16663260"))
        self.assertTrue(LineStickerUtils.is_sticker_exists(16663260))
        self.assertFalse(LineStickerUtils.is_sticker_exists("88"))
        self.assertFalse(LineStickerUtils.is_sticker_exists(88))
        self.assertFalse(LineStickerUtils.is_sticker_exists(True))

    def test_animated_download_get_integer_id(self):
        result = LineStickerUtils.download_apng_as_gif(15769, 248521690)

        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.conversion_result.succeed)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_apng(15769, 248521690) as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

        with LineStickerUtils.get_downloaded_apng_frames(15769, 248521690) as f:
            self.assertTrue(is_zipfile(f))
            self.assertGreaterEqual(len(ZipFile(f).namelist()), 0)

    def test_download_animated(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path)

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

            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.conversion_result.succeed)
            self.assertTrue(result.conversion_result.frame_zipping.success)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path)

            self.assertTrue(result.available)
            self.assertTrue(result.already_exists)
            self.assertIsNone(result.conversion_result)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

            self.assertTrue(is_zipfile(out_path_frames))
            self.assertGreaterEqual(len(ZipFile(out_path_frames).namelist()), 0)

    def test_download_animated_already_downloaded_gif(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path, with_frames=False)

            self.assertTrue(result.available)
            self.assertFalse(result.already_exists)
            self.assertTrue(result.conversion_result.succeed)
            self.assertFalse(result.conversion_result.frame_zipping.success)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))

            result = LineStickerUtils.download_apng_as_gif("15769", "248521690", out_path)

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

        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.conversion_result.succeed)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_apng("15769", "248521690") as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_download_animated_already_downloaded_output_path_not_given(self):
        result = LineStickerUtils.download_apng_as_gif("15769", "248521690")

        self.assertTrue(result.available)
        self.assertFalse(result.already_exists)
        self.assertTrue(result.conversion_result.succeed)
        self.assertTrue(result.succeed)

        result = LineStickerUtils.download_apng_as_gif("15769", "248521690")

        self.assertTrue(result.available)
        self.assertTrue(result.already_exists)
        self.assertIsNone(result.conversion_result)
        self.assertTrue(result.succeed)

        with LineStickerUtils.get_downloaded_apng("15769", "248521690") as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_download_animated_not_exists(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")

            result = LineStickerUtils.download_apng_as_gif("1", "1", out_path)

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

            self.assertFalse(result.available)
            self.assertIsNone(result.conversion_result)
            self.assertFalse(result.succeed)
            self.assertFalse(os.path.exists(out_path))

    def test_get_downloaded_animated(self):
        result = LineStickerUtils.download_apng_as_gif("15769", "248521690")

        self.assertTrue(result.available)
        self.assertTrue(result.conversion_result.frame_zipping.success)
        self.assertTrue(result.conversion_result.succeed)

        with LineStickerUtils.get_downloaded_apng("15769", "248521690") as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_get_downloaded_animated_not_downloaded(self):
        with LineStickerUtils.get_downloaded_apng("15769", "248521690") as f:
            self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_get_downloaded_animated_not_exists(self):
        self.assertIsNone(LineStickerUtils.get_downloaded_apng("1", "1"))

    def test_get_downloaded_animated_frames(self):
        result = LineStickerUtils.download_apng_as_gif("15769", "248521690")

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
