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
    return in_color # disabled

    # divide rgb and alpha
    in_rgb = in_color[:3]
    in_opa = in_color[-1:]

    primary_color = (100, 181, 246)
    secondary_color = (255, 255, 255)

    # rules
    # -------------
    # black - white -> primary - secondary
    # red, green, blue -> color_palette

    # grayscale spectrum -> Primary <-> Secondary
    if len(set(in_rgb)) == 1:
        factor = in_rgb[0] / 255
        slider = lambda x, y: int((1 - factor) * x + factor * y)
        zip_cols = zip(primary_color, secondary_color)
        final_rgb = [slider(p, s) for p, s in zip_cols]
        return tuple(final_rgb) + in_opa

    # no conditions met -> return original color
    return in_color


def create_icon_png_from_svg(in_file: str, render_size: vector.Pair) -> vector.RenderSurface:
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

    # svg processing
    svg_tree = parser.SVGParser(in_file)
    svg_bb = surface_bb.get_sub_bbox((svg_fraction, svg_fraction))

    # print("Drawing background")
    # print("--------------------")
    # imgdrawer.draw
    # print("--------------------")

    # print("Drawing vectors")
    # print("--------------------")
    for drw in svg_tree.draw_store:
        print(f"Drawing {drw.style.fillcolor}")
        v_transform = drw.get_transform(svg_bb)
        drw.draw(surface, transform=v_transform)
    # print("--------------------")
    # print("Successful!")

    return surface

