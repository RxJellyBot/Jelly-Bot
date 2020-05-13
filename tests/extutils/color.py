from extutils.color import ColorFactory, Color
from tests.base import TestCase


class TestColorFactory(TestCase):
    def test_color_factory_from_hex(self):
        clr_hex = ColorFactory.from_hex("#FFFFFF")
        self.assertEquals("#ffffff", clr_hex.color_hex)
        self.assertEquals(16777215, clr_hex.color_int)
        self.assertEquals(255, clr_hex.r)
        self.assertEquals(255, clr_hex.g)
        self.assertEquals(255, clr_hex.b)

        clr_hex = ColorFactory.from_hex("#ffffff")
        self.assertEquals("#ffffff", clr_hex.color_hex)
        self.assertEquals(16777215, clr_hex.color_int)
        self.assertEquals(255, clr_hex.r)
        self.assertEquals(255, clr_hex.g)
        self.assertEquals(255, clr_hex.b)

        clr_hex = ColorFactory.from_hex("323232")
        self.assertEquals("#323232", clr_hex.color_hex)
        self.assertEquals(3289650, clr_hex.color_int)
        self.assertEquals(50, clr_hex.r)
        self.assertEquals(50, clr_hex.g)
        self.assertEquals(50, clr_hex.b)

        clr_hex = ColorFactory.BLACK
        self.assertEquals("#000000", clr_hex.color_hex)
        self.assertEquals(0, clr_hex.color_int)
        self.assertEquals(0, clr_hex.r)
        self.assertEquals(0, clr_hex.g)
        self.assertEquals(0, clr_hex.b)

        with self.assertRaises(ValueError):
            ColorFactory.from_hex("GGGGGG")
        with self.assertRaises(ValueError):
            ColorFactory.from_hex("#AAA")
        with self.assertRaises(ValueError):
            ColorFactory.from_hex("AAA")
        with self.assertRaises(ValueError):
            ColorFactory.from_hex("167AGG")

    def test_color_factory_from_rgb(self):
        clr_hex = ColorFactory.from_rgb(255, 255, 255)
        self.assertEquals("#ffffff", clr_hex.color_hex)
        self.assertEquals(16777215, clr_hex.color_int)
        self.assertEquals(255, clr_hex.r)
        self.assertEquals(255, clr_hex.g)
        self.assertEquals(255, clr_hex.b)

        with self.assertRaises(ValueError):
            ColorFactory.from_rgb(255, 255, 256)
        with self.assertRaises(ValueError):
            ColorFactory.from_rgb(255, 256, 255)
        with self.assertRaises(ValueError):
            ColorFactory.from_rgb(256, 255, 255)
        with self.assertRaises(ValueError):
            ColorFactory.from_rgb(-1, 255, 255)
        with self.assertRaises(ValueError):
            ColorFactory.from_rgb(255, -1, 255)
        with self.assertRaises(ValueError):
            ColorFactory.from_rgb(255, 255, -1)


class TestColor(TestCase):
    def test_color(self):
        clr_hex = Color(0)
        self.assertEquals("#000000", clr_hex.color_hex)
        self.assertEquals(0, clr_hex.color_int)
        self.assertEquals(0, clr_hex.r)
        self.assertEquals(0, clr_hex.g)
        self.assertEquals(0, clr_hex.b)

        with self.assertRaises(ValueError):
            Color(16777216)
        with self.assertRaises(ValueError):
            Color(-1)

    def test_color_equals(self):
        clr_hex = Color(0)
        self.assertEquals(0, clr_hex)
        self.assertEquals(Color(0), clr_hex)
        self.assertEquals(ColorFactory.BLACK, clr_hex)
        self.assertEquals("#000000", clr_hex)
        self.assertEquals("000000", clr_hex)
        self.assertNotEquals(Color(1), clr_hex)

    def test_color_num_valid(self):
        self.assertTrue(Color.color_num_valid(0))
        self.assertTrue(Color.color_num_valid(16777215))
        self.assertFalse(Color.color_num_valid(-1))
        self.assertFalse(Color.color_num_valid(16777216))
