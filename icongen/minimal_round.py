# Minimal Round Icon Generator
# ----------------------------


from svg2png import parser
from svg2png import vector


def color_map(in_color: vector.RGBATuple) -> vector.RGBATuple:
    """
    Color map function for renderer
    -------------------------------
    - takes in and outputs rgba tuple
    """

    # divide rgb and alpha
    in_rgb = in_color[:3]
    in_opa = in_color[-1]

    primary_color = (239, 83, 80)
    secondary_color = (255, 255, 255)

    # rules
    # -------------
    # black - white -> primary - secondary
    # red, green, blue -> color_palette

    # grayscale spectrum -> primary <-> secondary
    if len(set(in_rgb)) == 1:
        factor = in_rgb[0] / 255
        slider = lambda x, y: int((1 - factor) * x + factor * y)
        zip_cols = zip(primary_color, secondary_color)
        final_rgb = [slider(p, s) for p, s in zip_cols]
        f_r, f_g, f_b = final_rgb
        return (f_r, f_g, f_b, in_opa)

    # pure red -> palette 1
    if in_rgb == (255, 0, 0):
        return (255, 207, 0, in_opa)

    # no conditions met -> return original color
    return in_color


def render_from_svg(in_file: str, render_size: vector.IntPair) -> vector.RenderSurface:
    """ Create a custom styled png from svg file """

    # DESIGN CORE PARAMETERS
    # ----------------------
    svg_fraction = 0.5
    circle_fraction = 0.8
    # ----------------------

    surface = vector.RenderSurface(render_size)
    surface_bb = vector.BBox(render_size)

    # color map to create dynamic colours from rules
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
