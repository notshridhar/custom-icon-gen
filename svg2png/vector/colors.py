from typing import Any, Tuple
import re


RGBATuple = Tuple[int, int, int, int]


def parse_color(color_str: str, opacity: int) -> RGBATuple:
    """
    Parse color string to get tuple(r,g,b,a)
    Uses opacity arg only if color string does not specify
    Fallback - transparent (0, 0, 0, 0)
    Returns tuple
    """

    # default
    a = opacity

    # lower case for simplicity
    color_str = color_str.lower()

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

    # fallback
    return (0, 0, 0, 0)


class Color:
    def __init__(self, col: Any = None, opacity: float = 1.0):
        """
        Construct color object from identifiers

        If no opacity is given, defaults to completely opaque
        If no color given, defaults to completely transparent

        Usage
        -------------------
        >>> Color("#12ab56")
        >>> Color("#124")
        """

        # default - transparent (black)
        rgba = (0, 0, 0, 0)
        alpha = int(opacity * 255)

        # nothing provided
        if not col:
            pass

        # string - parse color
        elif isinstance(col, str):
            rgba = parse_color(col, alpha)

        # rgb given as tuple or list
        elif isinstance(col, list) or isinstance(col, tuple):
            if len(col) == 3:
                r, g, b = map(int, col)
                rgba = (r, g, b, alpha)
            elif len(col) == 4:
                r, g, b, a = map(int, col)
                rgba = (r, g, b, a)

        # grayscale factor given
        elif isinstance(col, int) or isinstance(col, float):
            fac = int(col)
            rgba = (fac, fac, fac, alpha)

        # cannot decode
        else:
            raise TypeError("Invalid color constructor", col)

        # construct finally
        self.rgba = rgba
        self.r, self.g, self.b, self.a = rgba

    def __getitem__(self, key):
        return self.rgba[key]

    def __iter__(self):
        return iter(self.rgba)

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
    def opacity(self) -> float:
        return self.a / 255.0


# def blend_color(color1: Color, color2: Color, ratio: float) -> 
