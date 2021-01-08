# Minimal Round Icon Generator
# ----------------------------

from typing import cast

import random

from svg2png import parser
from svg2png import vector


CURRENT_PALETTE: dict = {}
PALETTES = [
    {
        "name": "blue",
        "primary": "#42a5f5",
        "secondary": "#ffffff",
        "extra1": "#ffd633", # yellow
        "extra2": "#5fc27b", # cyan
        "extra3": "#304fad", # indigo
    },
    {
        "name": "orange",
        "primary": "#ffbe0d",
        "secondary": "#ffffff",
        "extra1": "#fa5c00", # red
        "extra2": "#00d0fa", # blue
        "extra3": "#61ffbb", # green
    },
    {
        "name": "green",
        "primary": "#68cc16",
        "secondary": "#ffffff",
        "extra1": "#f5ff36", # yellow
        "extra2": "#38e4ff", # blue
        "extra3": "#ff8533", # orange
    },
    {
        "name": "purple",
        "primary": "#a743cf",
        "secondary": "#ffffff",
        "extra1": "#f554cd", # pink
        "extra2": "#54f5cf", # cyan
        "extra3": "#daf554", # yellow
    },
    {
        "name": "brown",
        "primary": "#a86448",
        "secondary": "#ffffff",
        "extra1": "#b5216d", # magenta
        "extra2": "#d1c627", # yellow
        "extra3": "#26d1b7", # cyan
    },
]


def color_map(in_color: vector.RGBATuple) -> vector.RGBATuple:
    """
    Color map function for renderer
    -------------------------------
    - takes in and outputs rgba tuple
    """

    # divide rgb and alpha
    in_rgb = in_color[:3]
    in_opa = in_color[-1]

    palette = CURRENT_PALETTE

    # rules
    # -------------
    # black - white -> primary - secondary
    # red, green, blue -> extra colors

    # grayscale spectrum -> primary <-> secondary
    if len(set(in_rgb)) == 1:
        factor = in_rgb[0] / 255
        slider = lambda x, y: int((1 - factor) * x + factor * y)
        prm_rgba = vector.parse_color(palette["primary"], in_opa)
        sec_rgba = vector.parse_color(palette["secondary"], in_opa)
        converted_rgba = tuple(slider(p, s) for p, s in zip(prm_rgba, sec_rgba))
        return cast(vector.RGBATuple, converted_rgba)

    # pure red -> extra 1
    if in_rgb == (255, 0, 0):
        return vector.parse_color(palette["extra1"], in_opa)
    
    # pure green -> extra 2
    if in_rgb == (0, 255, 0):
        return vector.parse_color(palette["extra2"], in_opa)

    # pure blue -> extra 3
    if in_rgb == (0, 0, 255):
        return vector.parse_color(palette["extra3"], in_opa)

    # no conditions met -> return original color
    return in_color


def render_from_svg(in_file: str, render_size: vector.IntPair) -> vector.RenderSurface:
    """ Create a custom styled png from svg file """

    global CURRENT_PALETTE

    # DESIGN CORE PARAMETERS
    # ----------------------
    svg_fraction = 0.5
    circle_fraction = 0.8
    # ----------------------

    surface = vector.RenderSurface(render_size)
    surface_bb = vector.BBox(render_size)

    # color map to create dynamic colours from rules
    CURRENT_PALETTE = random.choice(PALETTES)
    surface.set_color_map(color_map)

    # background circle
    circle = vector.DrawableEllipse("back-circle")
    circle.set_center(render_size[0] / 2)
    circle.set_radius(render_size[0] * circle_fraction / 2)
    circle.style.fillcolor = vector.Color("#000")
    circle.draw(surface)

    # svg processing
    draw_store = parser.parse_svg_file(in_file)
    svg_bb = surface_bb.get_sub_bbox((svg_fraction, svg_fraction))

    # draw svg on surface
    transform = draw_store.get_transform(svg_bb)
    draw_store.draw_all(surface, transform)

    return surface
