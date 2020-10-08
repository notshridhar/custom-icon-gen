import sys
from icongen import minimal_round


filepath = "./icons/svg/app_store.svg"
if len(sys.argv) >= 2:
    filepath = "./icons/svg/" + sys.argv[1] + ".svg"

image = minimal_round.render_from_svg(filepath, (1024, 1024))
image.save("test.png", (512, 512))
