import glob

from svg2png import parser
from svg2png import vector


svg_files = glob.glob("./tests/svg_files/*.svg")


# DRY RUN
# -------
for filename in svg_files:
    parser.parse_svg_file(filename)


# RENDER INTO PNG
# ---------------
for filename in svg_files:
    drawables = parser.parse_svg_file(filename)
    surface = vector.RenderSurface(drawables.canvas_size)
    drawables.draw_all(surface)
    outname = filename.replace(".svg", ".png")
    surface.save(outname, (300, 300))
