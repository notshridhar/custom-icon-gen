# Minimal Round Icon Generator
# ----------------------------


from svg2png import parser as svgparser
from svg2png import draw as imgdraw


def color_map(in_color: str) -> str:
    """
    Color map function for renderer
    --------------------------
    - takes and outputs hex color strings
    """

    # no point going through everything
    if not in_color:
        return in_color

    primary_color = "#64b5f6"
    secondary_color = "#ffffff"

    # rules
    # -------------
    # black - white -> primary - secondary
    # red, green, blue -> color_palette

    input_col_tup = svgparser.parse_hex_color(in_color)
    
    # return original color if parser got error
    if not input_col_tup:
        return in_color

    # grayscale spectrum -> Primary <-> Secondary
    if len(set(input_col_tup)) == 1:
        prm = svgparser.parse_hex_color(primary_color)
        sec = svgparser.parse_hex_color(secondary_color)

        factor = input_col_tup[0] / 255
        slider = lambda x, y: (1 - factor) * x + factor * y
        final_color = [slider(p, s) for p, s in zip(prm, sec)]

        return svgparser.create_hex_color(final_color)

    # no conditions -> return original color
    return in_color


def create_icon_png_from_svg(in_file: str, render_size: tuple) -> imgdraw.RenderSurface:
    """ Create a custom styled png from svg file """

    # DESIGN CORE PARAMETERS
    # ----------------------
    svg_fraction = 1.0
    circle_fraction = 0.8
    # ----------------------

    surface = imgdraw.RenderSurface(render_size)
    surface_bb = imgdraw.BoundingBox((0, 0) + render_size)

    # color map to create dynamic colours from rules
    surface.set_color_map(color_map)

    # svg processing
    svg_tree = svgparser.SVGParser(in_file)
    svg_bb = surface_bb.get_sub_bbox(svg_fraction)
    svg_vectors = svg_tree.get_drawables()
    
    # print("Drawing background")
    # print("--------------------")
    # imgdrawer.draw
    # print("--------------------")

    print("Drawing vectors")
    print("--------------------")
    for vector in svg_vectors:
        print("Drawing vector :", vector.id)
        v_transform = vector.get_transform(svg_bb)
        vector.draw(surface, transform=v_transform)
    print("--------------------")
    print("Successful!")

    return surface
