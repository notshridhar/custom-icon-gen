from icongen import minimal_round


RENDER_SIZE = (1200, 1200)
FINAL_SIZE = (400, 400)

image = minimal_round.render_from_svg("test.svg", RENDER_SIZE)
image.save("test.png", FINAL_SIZE)
