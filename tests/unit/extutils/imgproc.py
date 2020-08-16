import os
from tempfile import TemporaryDirectory
from zipfile import ZipFile, is_zipfile

from extutils.imgproc.apng2gif import convert, ConvertResult, ConvertOpResult
from tests.base import TestCase

__all__ = ["TestApng2Gif", "TestApng2GifConvertResult", "TestApng2GifConvertOpResult"]


class TestApng2Gif(TestCase):
    def test_convert(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            with open("tests/res/line_sticker.apng", "rb") as f:
                result = convert(f.read(), out_path, zip_frames=False)

            self.assertTrue(result.frame_extraction.success)
            self.assertGreaterEqual(result.frame_extraction.duration, 0)
            self.assertFalse(result.frame_zipping.success)
            self.assertEqual(result.frame_zipping.duration, 0)
            self.assertIsNone(result.frame_zipping.exception)
            self.assertTrue(result.image_data_collation.success)
            self.assertGreaterEqual(result.image_data_collation.duration, 0)
            self.assertTrue(result.gif_merging.success)
            self.assertGreaterEqual(result.gif_merging.duration, 0)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))
            self.assertFalse(os.path.exists(out_path_frames))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_convert_zip_frames(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            with open("tests/res/line_sticker.apng", "rb") as f:
                result = convert(f.read(), out_path)

            self.assertTrue(result.frame_extraction.success)
            self.assertGreaterEqual(result.frame_extraction.duration, 0)
            self.assertIsNone(result.frame_zipping.exception)
            self.assertTrue(result.frame_zipping.success)
            self.assertGreaterEqual(result.frame_zipping.duration, 0)
            self.assertTrue(result.image_data_collation.success)
            self.assertGreaterEqual(result.image_data_collation.duration, 0)
            self.assertTrue(result.gif_merging.success)
            self.assertGreaterEqual(result.gif_merging.duration, 0)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path), out_path)
            self.assertTrue(os.path.exists(out_path_frames), out_path_frames)

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

            self.assertTrue(is_zipfile(out_path_frames))
            self.assertGreaterEqual(len(ZipFile(out_path_frames).namelist()), 0)


class TestApng2GifConvertResult(TestCase):
    def test_succeed(self):
        result = ConvertResult()
        self.assertFalse(result.succeed)

        result.frame_extraction.set_success(0.0)
        self.assertFalse(result.succeed)

        result.frame_zipping.set_success(0.0)
        self.assertFalse(result.succeed)

        result.image_data_collation.set_success(0.0)
        self.assertFalse(result.succeed)

        result.gif_merging.set_success(0.0)
        self.assertTrue(result.succeed)

    def test_succeed_no_zip_frames(self):
        result = ConvertResult()
        self.assertFalse(result.succeed)

        result.frame_extraction.set_success(0.0)
        self.assertFalse(result.succeed)

        result.image_data_collation.set_success(0.0)
        self.assertFalse(result.succeed)

        result.gif_merging.set_success(0.0)
        self.assertTrue(result.succeed)

        self.assertFalse(result.frame_zipping.success)

    def test_succeed_set_success(self):
        result = ConvertResult()
        self.assertFalse(result.succeed)

        result.frame_extraction.set_success(0.1)
        self.assertFalse(result.succeed)

        result.image_data_collation.set_success(0.1)
        self.assertFalse(result.succeed)

        result.gif_merging.set_success(0.1)
        self.assertTrue(result.succeed)

        self.assertFalse(result.frame_zipping.success)


class TestApng2GifConvertOpResult(TestCase):
    def test_set_success(self):
        result = ConvertOpResult()

        self.assertFalse(result.success)
        self.assertEqual(result.duration, 0)
        self.assertIsNone(result.exception)

        result.set_success(0.7)

        self.assertTrue(result.success)
        self.assertEqual(result.duration, 0.7)
        self.assertIsNone(result.exception)

    def test_set_failed(self):
        result = ConvertOpResult()

        self.assertFalse(result.success)
        self.assertEqual(result.duration, 0)
        self.assertIsNone(result.exception)

        result.set_failure(ValueError())

        self.assertFalse(result.success)
        self.assertEqual(result.duration, 0.0)
        self.assertIsInstance(result.exception, ValueError)

    def test_set_failed_no_exception(self):
        result = ConvertOpResult()

        self.assertFalse(result.success)
        self.assertEqual(result.duration, 0)
        self.assertIsNone(result.exception)

        result.set_failure()

        self.assertFalse(result.success)
        self.assertEqual(result.duration, 0.0)
        self.assertIsNone(result.exception)

    def test_set_twice(self):
        result = ConvertOpResult()

        self.assertFalse(result.success)
        self.assertEqual(result.duration, 0)
        self.assertIsNone(result.exception)

        result.set_failure(ValueError())

        self.assertFalse(result.success)
        self.assertEqual(result.duration, 0.0)
        self.assertIsInstance(result.exception, ValueError)

        with self.assertRaises(ValueError):
            result.set_success(0.7)
        with self.assertRaises(ValueError):
            result.set_failure()

        self.assertFalse(result.success)
        self.assertEqual(result.duration, 0.0)
        self.assertIsInstance(result.exception, ValueError)

    def test_set_twice_2(self):
        result = ConvertOpResult()

        self.assertFalse(result.success)
        self.assertEqual(result.duration, 0)
        self.assertIsNone(result.exception)

        result.set_success(0.7)

        self.assertTrue(result.success)
        self.assertEqual(result.duration, 0.7)
        self.assertIsNone(result.exception)

        with self.assertRaises(ValueError):
            result.set_success(0.7)
        with self.assertRaises(ValueError):
            result.set_failure()

        self.assertTrue(result.success)
        self.assertEqual(result.duration, 0.7)
        self.assertIsNone(result.exception)
