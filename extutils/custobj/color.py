import re


class Color:
    def __init__(self, color_sum: int):
        if 0 <= color_sum <= 16777216:
            self._col_code = color_sum
        else:
            raise ValueError(f"Invalid `color_sum`. Should be 0~16777216. ({color_sum})")


class ColorFactory:
    BLACK = Color(0)

    @staticmethod
    def from_rgb(red: int, green: int, blue: int):
        def _val_check(val, name):
            if val < 0 or val > 256:
                raise ValueError(f"Invalid {name} value. Should be 0~256. ({val})")

        _val_check(red, "RED")
        _val_check(green, "GREEN")
        _val_check(blue, "BLUE")

        return Color(red * 65536 + green * 256 + blue)

    @staticmethod
    def from_hex(hex_str: str):
        """
        :param hex_str: Allowed formats are: #FFFFFF or FFFFFF.
        """
        if not re.match(r"#?[0-9A-Fa-f]{6}", hex_str):
            raise ValueError(f"Invalid color string. Should be like #FFFFFF or FFFFFF. ({hex_str})")

        hex_str = hex_str.replace("#", "")

        return ColorFactory.from_rgb(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))