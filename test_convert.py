import glob

from svg2png import parser
from svg2png import vector


render_size = (600, 600)
svg_files = glob.glob("./tests/svg_files/*.svg")


# DRY RUN
# -------
for filename in svg_files:
    svgtree = parser.SVGParser(filename)
    

# RENDER INTO PNG
# ---------------
for filename in svg_files:
    svgtree = parser.SVGParser(filename)
    surface = vector.RenderSurface(svgtree.canvas_size)
    for drw in svgtree.draw_store:
        drw.draw(surface)
    outname = filename.replace(".svg", ".png")
    surface.save(outname, (300, 300))
