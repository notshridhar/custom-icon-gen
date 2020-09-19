import sys
from icongen import minimal_round


RENDER_SIZE = (800, 800)
FINAL_SIZE = (400, 400)


filepath = "./icons/svg/app_store.svg"
if len(sys.argv) >= 2:
    filepath = "./icons/svg/" + sys.argv[1] + ".svg"

image = minimal_round.render_from_svg(filepath, RENDER_SIZE)
image.save("test.png", FINAL_SIZE)
