import re

from bson.codec_options import TypeEncoder


class Color:
    @staticmethod
    def color_num_valid(num: int):
        return 0 <= num <= 16777215

    def __init__(self, color_sum: int):
        """
        :exception ValueError: `color_sum` is invalid.
        """
        if Color.color_num_valid(color_sum):
            self._col_code = color_sum
        else:
            raise ValueError(f"Invalid `color_sum`. Should be 0~16777215. ({color_sum})")

    @property
    def color_int(self) -> int:
        return self._col_code

    @property
    def r(self) -> int:
        return self.color_int // 65536

    @property
    def g(self) -> int:
        return (self.color_int // 256) % 256

    @property
    def b(self) -> int:
        return self.color_int % 256

    @property
    def color_hex(self) -> str:
        """Return the color in the format of #FFFFFF."""
        return f"#{self.color_int // 65536:02x}{(self.color_int // 256) % 256:02x}{self.color_int % 256:02x}"

    def __repr__(self):
        return f"Color: {self.color_hex}"

    def __eq__(self, other):
        if isinstance(other, Color):
            return other.color_int == self.color_int
        elif isinstance(other, int):
            return other == self.color_int
        elif isinstance(other, str):
            return other.replace("#", "") == self.color_hex.replace("#", "")
        else:
            return False


class ColorFactory:
    BLACK = Color(0)
    WHITE = Color(16777215)

    DEFAULT = BLACK

    @staticmethod
    def from_rgb(red: int, green: int, blue: int):
        """
        :exception ValueError: if any or `red`, `green` or `blue` is invalid.
        """

        def _val_check_(val, name):
            if val < 0 or val > 255:
                raise ValueError(f"Invalid {name} value. Should be 0~255. ({val})")

        _val_check_(red, "RED")
        _val_check_(green, "GREEN")
        _val_check_(blue, "BLUE")

        return Color(red * 65536 + green * 256 + blue)

    @staticmethod
    def from_hex(hex_str: str):
        """
        :param hex_str: Allowed formats are: #FFFFFF or FFFFFF.
        :exception ValueError: if the hex string is in a invalid format.
        """
        if not re.match(r"#?[0-9A-Fa-f]{6}", hex_str):
            raise ValueError(f"Invalid color string. Should be in the format of #FFFFFF or FFFFFF. ({hex_str})")

        hex_str = hex_str.replace("#", "")

        return ColorFactory.from_rgb(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))


class ColorMongoEncoder(TypeEncoder):
    python_type = Color

    def transform_python(self, value):
        return value.color_int
