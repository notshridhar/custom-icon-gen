# Minimal Round Icon Generator
# ----------------------------


import random

from svg2png import parser
from svg2png import vector


CURRENT_PALETTE = {}
PALETTES = [
    {
        "name": "blue",
        "primary": "#1e88e5",
        "secondary": "#ffffff",
        "extra1": "#d81b60", # magenta
        "extra2": "#fb8c00", # yellow
        "extra3": "#7cb342", # green
    },
    {
        "name": "orange",
        "primary": "#fb8c00",
        "secondary": "#ffffff",
        "extra1": "#d81b60", # magenta
        "extra2": "#1e88e5", # blue
        "extra3": "#7cb342", # green
    },
    {
        "name": "green",
        "primary": "#689f38",
        "secondary": "#ffffff",
        "extra1": "#d81b60", # magenta
        "extra2": "#1e88e5", # blue
        "extra3": "#ffee58", # yellow
    },
    {
        "name": "purple",
        "primary": "#7b1fa2",
        "secondary": "#ffffff",
        "extra1": "#ff5722", # red
        "extra2": "#7cb342", # green
        "extra3": "#ffee58", # yellow
    },
    {
        "name": "brown",
        "primary": "#6d4c41",
        "secondary": "#ffffff",
        "extra1": "#4dd0e1", # cyan
        "extra2": "#fb8c00", # yellow
        "extra3": "#7cb342", # green
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
        return tuple(slider(p, s) for p, s in zip(prm_rgba, sec_rgba))

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
    circle = vector.DrawableEllipse("")
    circle.set_center(render_size[0] / 2)
    circle.set_radius(render_size[0] * circle_fraction / 2)
    circle.style.fillcolor = vector.Color("#000000")
    circle.draw(surface)

    # svg processing
    draw_store = parser.parse_svg_file(in_file)
    svg_bb = surface_bb.get_sub_bbox((svg_fraction, svg_fraction))

    # draw svg on surface
    transform = draw_store.get_transform(svg_bb)
    draw_store.draw_all(surface, transform)

    return surface
