from datetime import datetime
import os
from tempfile import TemporaryDirectory
from zipfile import ZipFile, is_zipfile

from flags import ImageContentType
from extutils.imgproc import ImgurClient, ImageContentProcessor
from extutils.imgproc.apng2gif import convert, ConvertResult
from tests.base import TestCase

__all__ = ["TestImgurClient", "TestApng2Gif", "TestApng2GifConvertResult"]


class TestImgurClient(TestCase):
    def cleanup(self, del_hash: str):
        result = ImgurClient.delete_image(del_hash)
        self.assertTrue(result, "Failed to delete the test image.")

    def test_image_upload_no_title_desc(self):
        url = "https://raw.githubusercontent.com/RaenonX/Jelly-Bot/master/tests/res/1x1.png"
        type_ = ImageContentType.URL.key

        result = ImgurClient.upload_image(url, type_)
        self.assertEqual(200, result.status, f"Image upload status not 200 ({result.status}).")
        self.assertTrue(result.success, "Image upload not success.")
        self.assertIsNotNone(result.link, "No image link returned.")

        self.cleanup(result.delete_hash)

    def test_image_upload_url(self):
        url = "https://raw.githubusercontent.com/RaenonX/Jelly-Bot/master/tests/res/1x1.png"
        type_ = ImageContentType.URL.key
        txt = f"Jelly Bot test upload on {datetime.now()}"

        result = ImgurClient.upload_image(url, type_, txt, txt)
        self.assertEqual(200, result.status, f"Image upload status not 200 ({result.status}).")
        self.assertTrue(result.success, "Image upload not success.")
        self.assertIsNotNone(result.link, "No image link returned.")

        self.cleanup(result.delete_hash)

    def test_image_upload_b64(self):
        img = ImageContentProcessor.local_img_to_base64_str("tests/res/1x1.png")
        type_ = ImageContentType.BASE64.key
        txt = f"Jelly Bot test upload on {datetime.now()}"

        result = ImgurClient.upload_image(img, type_, txt, txt)
        self.assertEqual(200, result.status, f"Image upload status not 200 ({result.status}).")
        self.assertTrue(result.success, "Image upload not success.")
        self.assertIsNotNone(result.link, "No image link returned.")

        self.cleanup(result.delete_hash)


class TestApng2Gif(TestCase):
    def test_convert(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            result = convert("tests/res/line_sticker.apng", out_path, zip_frames=False)

            self.assertTrue(result.input_exists)
            self.assertTrue(result.frame_extracted)
            self.assertGreaterEqual(result.frame_extraction_duration, 0)
            self.assertFalse(result.frame_zipped)
            self.assertEqual(result.frame_zipping_time, 0)
            self.assertIsNone(result.frame_zipping_exception)
            self.assertTrue(result.image_data_acquired)
            self.assertGreaterEqual(result.image_data_acquisition_duration, 0)
            self.assertTrue(result.gif_merged)
            self.assertGreaterEqual(result.gif_merge_duration, 0)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path))
            self.assertFalse(os.path.exists(out_path_frames))

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

    def test_convert_zip_frames(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")
            out_path_frames = os.path.join(temp_dir, "out-frames.zip")

            result = convert("tests/res/line_sticker.apng", out_path)

            self.assertTrue(result.input_exists)
            self.assertTrue(result.frame_extracted)
            self.assertGreaterEqual(result.frame_extraction_duration, 0)
            self.assertIsNone(result.frame_zipping_exception)
            self.assertTrue(result.frame_zipped)
            self.assertGreaterEqual(result.frame_zipping_time, 0)
            self.assertTrue(result.image_data_acquired)
            self.assertGreaterEqual(result.image_data_acquisition_duration, 0)
            self.assertTrue(result.gif_merged)
            self.assertGreaterEqual(result.gif_merge_duration, 0)
            self.assertTrue(result.succeed)
            self.assertTrue(os.path.exists(out_path), out_path)
            self.assertTrue(os.path.exists(out_path_frames), out_path_frames)

            with open(out_path, "rb") as f:
                self.assertTrue(f.read(6) in (b"GIF87a", b"GIF89a"))

            self.assertTrue(is_zipfile(out_path_frames))
            self.assertGreaterEqual(len(ZipFile(out_path_frames).namelist()), 0)

    def test_convert_no_apng(self):
        with TemporaryDirectory() as temp_dir:
            out_path = os.path.join(temp_dir, "out.gif")

            result = convert("tests/res/oops", out_path)

            self.assertFalse(result.input_exists)
            self.assertFalse(result.frame_extracted)
            self.assertFalse(result.frame_zipped)
            self.assertFalse(result.image_data_acquired)
            self.assertFalse(result.gif_merged)
            self.assertFalse(result.succeed)
            self.assertFalse(os.path.exists(out_path))
            self.assertFalse(os.path.exists(os.path.join(out_path, "out-frames.zip")))


class TestApng2GifConvertResult(TestCase):
    def test_succeed(self):
        result = ConvertResult()
        self.assertFalse(result.succeed)

        result.frame_extracted = True
        self.assertFalse(result.succeed)

        result.frame_zipped = True
        self.assertFalse(result.succeed)

        result.image_data_acquired = True
        self.assertFalse(result.succeed)

        result.gif_merged = True
        self.assertTrue(result.succeed)

    def test_succeed_no_zip_frames(self):
        result = ConvertResult()
        self.assertFalse(result.succeed)

        result.frame_extracted = True
        self.assertFalse(result.succeed)

        result.image_data_acquired = True
        self.assertFalse(result.succeed)

        result.gif_merged = True
        self.assertTrue(result.succeed)

        self.assertFalse(result.frame_zipped)
