from datetime import datetime

from flags import ImageContentType
from extutils.imgproc import ImgurClient, ImageContentProcessor
from tests.base import TestCase

__all__ = ["TestImgurClient"]


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
