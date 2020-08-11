import abc
from typing import Optional

from PIL import Image, ImageChops

from tests.base import TestCase


class TestImageComparisonMixin(TestCase, abc.ABC):
    def assertImageEqual(self, a: Image.Image, b: Image.Image, msg: Optional[str] = None):
        self.assertIsNone(ImageChops.difference(a, b).getbbox(), msg)
