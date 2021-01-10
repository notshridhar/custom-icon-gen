from typing import cast, Tuple, Union, Iterable

import re
import math


Number = Union[int, float]
RGBATuple = Tuple[int, int, int, int]
ColorOptions = Union[str, Iterable, Number]


def parse_color(color_str: str, alpha: int = 255) -> RGBATuple:
    """
    Parse color string.
    alpha parameter is used if color string does not specify it.
    Returns tuple (r, g, b, a).

    Formats supported -
    - Names [ white | black | transparent ]
    - Hex codes [ #rgb | #rgba | #rrggbb | #rrggbbaa ]
    """

    # case independent parsing
    color_str = color_str.lower()

    # named colors
    named_colors = {
        "white": (255, 255, 255, alpha),
        "black": (0, 0, 0, alpha),
        "transparent": (0, 0, 0, 0),
    }
    if color_str in named_colors:
        return named_colors[color_str]

    # 3 digit hex code
    if re.match("#[a-f0-9]{3}$", color_str):
        r = int(color_str[1] * 2, 16)
        g = int(color_str[2] * 2, 16)
        b = int(color_str[3] * 2, 16)
        return (r, g, b, alpha)

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
        return (r, g, b, alpha)

    # 8 digit hex code
    if re.match("#[a-f0-9]{8}$", color_str):
        r = int(color_str[1:3], 16)
        g = int(color_str[3:5], 16)
        b = int(color_str[5:7], 16)
        a = int(color_str[7:9], 16)
        return (r, g, b, a)

    raise ValueError(f"cannot parse color - {color_str}")


class Color:
    def __init__(self, col: ColorOptions = "transparent", opacity: Number = 1):
        """
        Color
        -----

        Formats supported -
        - Names
        - Hex codes
        - Sequence (r, g, b)
        - Grayscale Factor (f)
        """

        alpha = int(opacity * 255)

        # parse color string
        if isinstance(col, str):
            self.r, self.g, self.b, self.a = parse_color(col, alpha)
            return

        # try unpacking
        if isinstance(col, tuple) or isinstance(col, list):
            self.r, self.g, self.b = cast(tuple, col)
            self.a = alpha
            return

        # grayscale
        if isinstance(col, int) or isinstance(col, float):
            fac = int(col)
            self.r, self.g, self.b, self.a = fac, fac, fac, alpha
            return

        raise ValueError(f"Cannot decode color - {col}")

    def as_hex(self) -> str:
        """ Get rgb hex string (omit opacity) """
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

    @classmethod
    def blend(cls, col1: "Color", col2: "Color", fac: Number) -> "Color":
        slider = lambda x: int(x[0] * fac + x[1] * (1 - fac))
        blend_rgba = tuple(map(slider, zip(col1.rgba, col2.rgba)))
        return Color(blend_rgba[:-1], blend_rgba[-1])


class LinearGradient:
    def __init__(self, col1: ColorOptions, col2: ColorOptions, direction: Number = 0):
        self.color1 = Color(col1)
        self.color2 = Color(col2)
        self.direction = direction

    def bake(self, w: int, h: int, scale=1.0, resolution=100):
        # constant [deps: direction]
        self._cos_t = math.cos(math.radians(self.direction))
        self._sin_t = math.sin(math.radians(self.direction))

        # constant [deps: w, h, direction, multiplier]
        max_r = w * self._cos_t + h * self._sin_t
        k = 2.0 * scale / max_r

        # function to get color from r
        def blender(r):
            r_adj = k * (r - max_r / 2)
            blend_fac = (1 + r_adj / math.sqrt(1 + r_adj ** 2)) / 2
            return Color.blend(self.color1, self.color2, blend_fac).rgba

        # construct table with discrete chunks for color lookup
        # given r -> obtain color
        linspace = [i * max_r / resolution for i in range(resolution + 1)]
        color_cache = list(map(blender, linspace))
        self._col_lookup = lambda r: color_cache[round(r * resolution / max_r)]

    def calculate2D(self, x: int, y: int) -> RGBATuple:
        return self._col_lookup(x * self._cos_t + y * self._sin_t)
