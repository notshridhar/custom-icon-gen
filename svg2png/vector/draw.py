# Drawing Module
# -----------
# Functions and classes for drawing


from typing import Optional, Union
from typing import Tuple, List, Dict, Sequence

from copy import deepcopy
from abc import abstractmethod, ABC

from PIL import Image, ImageDraw  # type: ignore
from PIL.Image import Image as PILImage  # type: ignore

from .base import Point, Transform

# type hints
Number = Union[int, float]
Pair = Tuple[Number, Number]


# DRAWABLE OBJECTS
# =====================
class DrawableStyle:
    def __init__(self, attrib: dict = {}):
        self.fillcolor = ""
        self.update(attrib)

    def update(self, attrib: dict):
        """
        Updates style inplace
        update policy: override [newer first]
        """
        tot_opa = float(attrib.get("opacity", 1))
        fill_opa = float(attrib.get("fill-opacity", 1)) * tot_opa
        fill_col = attrib.get("fill", self.fillcolor) if fill_opa else ""
        self.fillcolor = fill_col

    def as_dict(self) -> dict:
        return {
            "fill": self.fillcolor,
            "fill-opacity": 1,
        }

    def copy(self) -> "DrawableStyle":
        return deepcopy(self)


class Drawable(ABC):
    def __init__(self, elem_id: str):
        self.elem_id = elem_id
        self.style = DrawableStyle()

    def set_style(self, attrib: dict):
        self.style = DrawableStyle(attrib)

    def copy(self):
        return deepcopy(self)

    @abstractmethod
    def draw(self, imdraw: ImageDraw, transform=Transform()):
        """ Handle drawing on surface (abstract) """
        pass


class DrawablePath(Drawable):
    def __init__(self, elem_id: str):
        super().__init__(elem_id)

        # core
        self.subpaths: List[List[Point]] = []

        # optimization
        self.curve_resolution = 1

        # state
        self.current_pos = Point((0, 0))

    def moveto(self, dest: Pair, rel=False):
        dest_pt = (Point(dest) + self.current_pos) if rel else Point(dest)
        self.subpaths.append([dest_pt])
        self.current_pos = dest_pt

    def lineto(self, dest: Pair, rel=False):
        dest_pt = (Point(dest) + self.current_pos) if rel else Point(dest)
        current_subpath = self.subpaths[-1]
        current_subpath.append(dest_pt)
        self.current_pos = dest_pt

    def curveto(self, handle1: Pair, handle2: Pair, dest: Pair, rel=False):
        p0 = self.current_pos
        p1 = (Point(handle1) + self.current_pos) if rel else Point(handle1)
        p2 = (Point(handle2) + self.current_pos) if rel else Point(handle2)
        p3 = (Point(dest) + self.current_pos) if rel else Point(dest)

        resolution = 10
        params = (i / resolution for i in range(1, resolution + 1))

        for t in params:
            c = [(1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3]
            bx = c[0] * p0.x + c[1] * p1.x + c[2] * p2.x + c[3] * p3.x
            by = c[0] * p0.y + c[1] * p1.y + c[2] * p2.y + c[3] * p3.y

            current_path = self.subpaths[-1]
            current_path.append(Point((bx, by)))

        self.current_pos = p3

    def closepath(self):
        current_subpath = self.subpaths[-1]
        dest = current_subpath[0]
        current_subpath.append(dest)
        self.current_pos = dest

    def draw(self, imdraw: ImageDraw, transform=Transform()):
        """ Draw path on the image """

        # skip transparent
        fillcol = self.style.fillcolor
        if not fillcol:
            return

        # filter closable paths for drawing
        closed_paths = filter(lambda x: len(x) > 2, self.subpaths)

        # apply transforms and draw
        for path in closed_paths:
            path_tuple = [tuple(p.transform(transform)) for p in path]
            imdraw.polygon(path_tuple, fill=fillcol)


# OBJECT STORAGE
# =====================
class DrawableObjectStore:
    def __init__(self, canvas: Tuple[int, int]):

        self.canvas_size = Point(canvas)

        # drawables stored in drawing order
        self._objects: List[Drawable] = []

        # stored in dict for lookup by id
        # contains objects with id
        self._named: Dict[str, Drawable] = {}

    def __getitem__(self, key):
        return self._objects[key]

    def __iter__(self):
        return iter(self._objects)

    def __len__(self):
        return len(self._objects)

    def append(self, elem_id: str, obj: Drawable, render=True):
        """
        if render=False, object is not added to render list
        """

        # save object with id
        if elem_id in self._named:
            raise ValueError("id already defined")
        elif elem_id:
            self._named[elem_id] = obj

        # append as renderable if render=True
        if render:
            self._objects.append(obj)

    def get(self, elem_id: str) -> Drawable:
        return self._named[elem_id]

    def clear(self):
        self._objects.clear()
        self._named.clear()

    def draw_all(
        self,
        image: Optional[PILImage] = None,
        bounding_box: Optional[Sequence[float]] = None,
    ) -> PILImage:
        """
        Draw all the drawables onto given image inside bounding box.
        If image is not given, creates a new image.
        Modifies image inplace and also returns it.
        """

        # get or construct image
        image = image or Image.new("RGBA", self.canvas_size)
        imdraw = ImageDraw.Draw(image)

        # construct transform if bbox given
        if bounding_box:
            left, top, width, height = bounding_box
            offset = (left, top)
            scale = (width / self.canvas_size.x, height / self.canvas_size.y)
            transform = Transform(offset, scale)
        else:
            transform = Transform()

        # draw all
        for drw in self._objects:
            drw.draw(imdraw, transform)

        return image
