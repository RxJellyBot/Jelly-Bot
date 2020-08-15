"""Module of various operations related to :class:`Color`."""
import re

from bson.codec_options import TypeEncoder


class Color:
    """
    Class representing a color.

    During constuction, if ``color_sum`` is invalid, :class:`ValueError` will be raised.

    :raises ValueError: `color_sum` is invalid
    """

    @staticmethod
    def color_num_valid(num: int) -> bool:
        """
        Check if the color number ``num`` is within the valid range.

        :param num: color number to be checked
        :return: if `num` is valid
        """
        return 0 <= num <= 16777215

    def __init__(self, color_sum: int):
        if Color.color_num_valid(color_sum):
            self._col_code = color_sum
        else:
            raise ValueError(f"Invalid `color_sum`. Should be 0~16777215. ({color_sum})")

    @property
    def color_int(self) -> int:
        """
        The sum of the color (R * 65536 + G * 256 + B).

        :return: the color code sum
        """
        return self._col_code

    @property
    def r(self) -> int:  # pylint: disable=C0103
        """
        Red value of RGB of the color.

        :return: red value
        """
        return self.color_int // 65536

    @property
    def g(self) -> int:  # pylint: disable=C0103
        """
        Green value of RGB of the color.

        :return: green value
        """
        return (self.color_int // 256) % 256

    @property
    def b(self) -> int:  # pylint: disable=C0103
        """
        Blue value of RGB of the color.

        :return: blue value
        """
        return self.color_int % 256

    @property
    def color_hex(self) -> str:
        """
        Return the color in the format of #FFFFFF.

        :return: hex color code with # prefixed
        """
        return f"#{self.color_int // 65536:02x}{(self.color_int // 256) % 256:02x}{self.color_int % 256:02x}"

    def __repr__(self):
        return f"Color: {self.color_hex}"

    def __hash__(self):
        return hash(self.color_int)

    def __eq__(self, other):
        if isinstance(other, Color):
            return other.color_int == self.color_int

        if isinstance(other, int):
            return other == self.color_int

        if isinstance(other, str):
            return other.replace("#", "") == self.color_hex.replace("#", "")

        return False


class ColorFactory:
    """Factory class to generate :class:`Color`."""

    BLACK = Color(0)
    WHITE = Color(16777215)

    DEFAULT = BLACK

    @staticmethod
    def from_rgb(red: int, green: int, blue: int) -> Color:
        """
        Generate a :class:`Color` from RGB.

        :return: a `Color` with using the provided RGB values
        :raises ValueError: any of `red`, `green` or `blue` is invalid
        """

        def _val_check(val, name):
            if val < 0 or val > 255:
                raise ValueError(f"Invalid {name} value. Should be 0~255. ({val})")

        _val_check(red, "RED")
        _val_check(green, "GREEN")
        _val_check(blue, "BLUE")

        return Color(red * 65536 + green * 256 + blue)

    @staticmethod
    def from_hex(hex_str: str) -> Color:
        """
        Generate a :class:`Color` from hex color string ``hex_str``.

        Allowed formats for ``hex_str`` are: #FFFFFF or FFFFFF.

        :param hex_str: hex color string to be used to generate a color
        :raises ValueError: hex string is in a invalid format
        """
        if not re.match(r"#?[0-9A-Fa-f]{6}", hex_str):
            raise ValueError(f"Invalid color string. Should be in the format of #FFFFFF or FFFFFF. ({hex_str})")

        hex_str = hex_str.replace("#", "")

        return ColorFactory.from_rgb(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))


class ColorMongoEncoder(TypeEncoder):
    """:class:`TypeEncoder` for MongoDB to handle the type of :class:`ColorMongoEncoder`."""

    python_type = Color

    def transform_python(self, value):
        return value.color_int
