from typing import cast, Tuple, Union, Iterable
import re


Number = Union[int, float]
RGBATuple = Tuple[int, int, int, int]
ColorOptions = Union[str, Number, Iterable]


def parse_color(color_str: str, opacity: int) -> RGBATuple:
    """
    Parse color string to get tuple(r,g,b,a)
    Uses opacity arg only if color string does not specify
    Fallback - transparent (0, 0, 0, 0)
    Returns tuple
    """
    a = opacity

    # lower case for simplicity
    color_str = color_str.lower()

    # named colors
    named_colors = {
        "white": (255, 255, 255, a),
        "black": (0, 0, 0, a),
        "transparent": (0, 0, 0, 0),
    }
    if color_str in named_colors:
        return named_colors[color_str]

    # 3 digit hex code
    if re.match("#[a-f0-9]{3}$", color_str):
        r = int(color_str[1] * 2, 16)
        g = int(color_str[2] * 2, 16)
        b = int(color_str[3] * 2, 16)
        return (r, g, b, a)

    # 4 digit hex code
    if re.match("#[a-f0-9]{4}$", color_str):
        r = int(color_str[1] * 2, 16)
        g = int(color_str[2] * 2, 16)
        b = int(color_str[3] * 2, 16)
        a = int(color_str[4] * 2, 16)
        return (r, g, b, a)

    # 6 digit hex code
    if re.match("#[a-f0-9]{6}$", color_str):
        r = int(color_str[1:3], 16)
        g = int(color_str[3:5], 16)
        b = int(color_str[5:7], 16)
        return (r, g, b, a)

    # 8 digit hex code
    if re.match("#[a-f0-9]{8}$", color_str):
        r = int(color_str[1:3], 16)
        g = int(color_str[3:5], 16)
        b = int(color_str[5:7], 16)
        a = int(color_str[7:9], 16)
        return (r, g, b, a)

    raise ValueError(f"cannot parse color - {color_str}")


class Color:
    def __init__(self, col: ColorOptions = "transparent", opacity: Number = 1.0):
        """
        Construct color object from identifiers
        -------------------

        If no opacity is given, defaults to completely opaque
        If no color given, defaults to completely transparent

        Usage
        -------------------
        >>> Color("#12ab56")
        >>> Color("#124")
        """

        alpha = int(opacity * 255)

        # try to parse color as string
        try:
            self.r, self.g, self.b, self.a = parse_color(cast(str, col), alpha)
            return
        except ValueError:
            pass

        # try to unpack
        try:
            self.r, self.g, self.b = cast(tuple, col)
            self.a = alpha
            return
        except ValueError:
            pass

        # grayscale
        if isinstance(col, int) or isinstance(col, float):
            fac = int(col)
            self.r, self.g, self.b, self.a = fac, fac, fac, alpha
            return

        raise ValueError(f"Cannot decode color - {col}")

    def __str__(self):
        hex_str = "#"
        for i in self.rgba[:3]:
            if i >= 256:
                raise ValueError
            hex_str += hex(i)[2:].zfill(2)
        return f"hex:{hex_str} alpha:{self.rgba[-1]}"

    def as_hex(self) -> str:
        """ Get RGB hex string """
        hex_str = "#"
        for i in self.rgba[:3]:
            if i >= 256:
                raise ValueError
            hex_str += hex(i)[2:].zfill(2)
        return hex_str

    @property
    def rgba(self) -> RGBATuple:
        return (self.r, self.g, self.b, self.a)

    @property
    def opacity(self) -> float:
        return self.a / 255.0
