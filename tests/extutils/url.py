from django.test import TestCase

from extutils.url import is_valid_url

__all__ = ["TestValidUrl"]


class TestValidUrl(TestCase):
    def test_valid_urls(self):
        urls = (
            "https://google.com",
            "https://facebook.com"
        )

        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(is_valid_url(url))

    def test_invalid_urls(self):
        urls = (
            "A",
            "https://"
        )

        for url in urls:
            with self.subTest(url=url):
                self.assertFalse(is_valid_url(url))
