# Minimal Round Icon Generator
# ----------------------------

import random

from svg2png import parser
from svg2png import vector


def render_from_svg(in_file: str, render_size: vector.IntPair) -> vector.RenderSurface:
    """ Create a custom styled png from svg file """

    # DESIGN CORE PARAMETERS
    # ----------------------
    svg_fraction = 0.5

    surface = vector.RenderSurface(render_size)
    surface_bb = vector.BBox(render_size)

    # svg processing
    draw_store = parser.parse_svg_file(in_file)
    svg_bb = surface_bb.get_sub_bbox((svg_fraction, svg_fraction))

    # draw svg on surface
    transform = draw_store.get_transform(svg_bb)
    draw_store.draw_all(surface, transform)

    return surface
