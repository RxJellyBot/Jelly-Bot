from flags import AutoReplyContentType
from models.utils import AutoReplyValidator
from tests.base import TestCase

__all__ = ["TestAutoReplyValidator"]


class TestAutoReplyValidator(TestCase):
    def test_validate_text(self):
        content_to_check = (
            ("", False),
            ("X", True),
            ("%*#&%#", True),
            ("-", True),
            (" ", False),
        )

        for content, expected_outcome in content_to_check:
            with self.subTest(content=content, expected_outcome=expected_outcome):
                self.assertEquals(
                    AutoReplyValidator.is_valid_content(
                        AutoReplyContentType.TEXT, content, online_check=True),
                    expected_outcome)
            with self.subTest(content=content, expected_outcome=expected_outcome):
                self.assertEquals(
                    AutoReplyValidator.is_valid_content(
                        AutoReplyContentType.TEXT, content, online_check=False),
                    expected_outcome)

    def test_validate_image(self):
        content_to_check = (
            ("", False, False),
            ("X", False, False),
            ("%*#&%#", False, False),
            ("-", False, False),
            ("https://cdn.discordapp.com/attachments/141403930176389120/"
             "708964350173511711/Screenshot_20200507-123028165.jpg", True, True),
            ("https://cdn.discordapp.com/attachments/631987269708021770/"
             "707761291720261662/Screenshot_20200506-201149.png", True, True),
            ("https://i.imgur.com/o4vvhXy.jpg", True, True),
            ("https://google.com", False, False),
            ("https://a.png", False, True),
        )

        for content, expected_online, expected_offline in content_to_check:
            with self.subTest(content=content, expected_online=expected_online):
                self.assertEquals(
                    AutoReplyValidator.is_valid_content(
                        AutoReplyContentType.IMAGE, content, online_check=True),
                    expected_online)
            with self.subTest(content=content, expected_offline=expected_offline):
                self.assertEquals(
                    AutoReplyValidator.is_valid_content(
                        AutoReplyContentType.IMAGE, content, online_check=False),
                    expected_offline)

    def test_validate_line_sticker(self):
        content_to_check = (
            ("3190323", True, True),
            ("87", False, True),
            ("A", False, False)
        )

        for content, expected_online, expected_offline in content_to_check:
            with self.subTest(content=content, expected_online=expected_online):
                self.assertEquals(
                    AutoReplyValidator.is_valid_content(
                        AutoReplyContentType.LINE_STICKER, content, online_check=True),
                    expected_online)
            with self.subTest(content=content, expected_offline=expected_offline):
                self.assertEquals(
                    AutoReplyValidator.is_valid_content(
                        AutoReplyContentType.LINE_STICKER, content, online_check=False),
                    expected_offline)
