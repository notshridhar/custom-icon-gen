# Minimal Round Icon Generator
# ----------------------------

from typing import Optional, Tuple

import random
import math

from PIL import Image  # type: ignore
from PIL.Image import Image as PILImage  # type: ignore

from svg2png import parser

from .palette import PALETTES
from .utils import Color, LinearGradient, BBox

# type hints
IntPair = Tuple[int, int]
RGBATuple = Tuple[int, int, int, int]


CURRENT_PALETTE: dict = {}


class ColorMap:
    def __init__(self):
        self.palette = CURRENT_PALETTE
        self.extra1 = Color(self.palette["extra1"]).rgba

    def remap(self, in_color: RGBATuple) -> RGBATuple:
        """ Remap colours """

        # early stop for transparent
        if not in_color[3]:
            return in_color

        # rule1: black <-> white => transparent <-> white
        if in_color[0] == in_color[1] == in_color[2]:
            f = in_color[0]
            return (f, f, f, f)

        # rule2: pure r/g/b -> extra colors
        if in_color[0] == 255 and in_color[1] == in_color[2] == 0:
            return self.extra1

        # no conditions met -> return original color
        return in_color


def draw_circle(image: Image, radius: float, outline: float):
    w, h = image.width, image.height

    _, col1, col2 = CURRENT_PALETTE["primary"].split(" ")
    lin_grad = LinearGradient(col1, col2, 90)
    lin_grad.bake(w, h, scale=1, resolution=100)

    def get_circle_pixel(i):
        y, x = i // w, i % w
        dist_2 = (x - w / 2) ** 2 + (y - h / 2) ** 2

        # interior
        rad_2 = (radius * w / 2) ** 2
        if dist_2 <= rad_2:
            return lin_grad.calculate2D(x, y)

        # outline
        out_2 = (outline * w / 2) ** 2
        if dist_2 <= out_2:
            return (255,) * 4

        # exterior
        return (0, 0, 0, 0)

    circle_pixels = list(map(get_circle_pixel, range(w * h)))
    image.putdata(circle_pixels)


def render_svg(
    path: str, render_size: IntPair, color_scheme: Optional[str] = None
) -> PILImage:
    """ Create a custom styled png from svg file """

    global CURRENT_PALETTE

    # Design Parameters
    # ---------------------
    svg_fraction = 0.5
    circle_fraction = 0.77
    outline_fraction = 0.83
    # ---------------------

    # set color scheme
    color_scheme = color_scheme or random.choice(list(PALETTES.keys()))
    CURRENT_PALETTE = PALETTES[color_scheme]

    # render at twice the final size
    initial_size = tuple(map(lambda x: x * 2, render_size))

    # create surface with background circle
    surface_bb = BBox(initial_size)
    surface_im = Image.new("RGBA", initial_size)
    draw_circle(surface_im, circle_fraction, outline_fraction)

    # draw svg on separate image for remapping
    svg_im = Image.new("RGBA", initial_size)
    svg_bb = surface_bb.get_sub_bbox(svg_fraction)
    draw_store = parser.parse_svg_file(path)
    draw_store.draw_all(svg_im, tuple(svg_bb))

    # remap svg colors
    pixdata = svg_im.load()
    cmap = ColorMap()
    for j in range(svg_im.height):
        for i in range(svg_im.width):
            pixdata[i, j] = cmap.remap(pixdata[i, j])

    # paste svg on background image
    surface_im.alpha_composite(svg_im)

    # downsample with BICUBIC filter
    return surface_im.resize(render_size, resample=Image.BICUBIC)
