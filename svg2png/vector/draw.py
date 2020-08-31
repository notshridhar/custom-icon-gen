# Drawing Module
# -----------
# Functions and classes for drawing


from typing import Optional, Union
from typing import Tuple, List, Callable, Any

from copy import deepcopy
from PIL import Image, ImageDraw # type: ignore

from .base import Point, Transform, BBox
from .colors import Color


# type hints
Num = Union[int, float]
Pair = Tuple[Num, Num]


# SURFACE
# =======================================
class RenderSurface:
    """
    Wrapper class around PIL.Image
    ------------------------------
    Mode = RGBA
    """

    def __init__(self, size: Pair):
        self.image = Image.new("RGBA", size)
        self.draw = ImageDraw.Draw(self.image)

        # color mapping function (callable)
        self.cmap = lambda x: x

    def set_color_map(self, color_map: Callable):
        """
        Set function to generate output color from rules
        color_map(str) -> str
        """
        self.cmap = color_map

    def save(self, filename: str, final_size: Optional[Pair] = None):
        """
        Save the rendered image with optional anti-aliasing
        If final size is given, saves resized image with antialiasing
        """
        if final_size:
            resized = self.image.resize(final_size, resample=Image.ANTIALIAS)
            resized.save(filename, "PNG")
        else:
            self.image.save(filename, "PNG")


# DRAWABLE OBJECTS
# =======================================
class DrawableStyle:
    def __init__(self, attribs: dict = {}):

        self.fillcolor = Color()
        self.linecolor = Color("#000000")

        self.update(attribs)

    def update(self, attribs: dict):
        """
        Updates style inplace
        update policy: override [newer first]
        """
        fill = attribs.get("fill", "")
        stroke = attribs.get("stroke", "")
        tot_o = float(attribs.get("opacity", 1.0))
        fill_o = float(attribs.get("fill-opacity", 1.0)) * tot_o
        stroke_o = float(attribs.get("stroke-opacity", 1.0)) * tot_o

        if fill:
            self.fillcolor = Color(fill, opacity=fill_o)

        if stroke:
            self.linecolor = Color(stroke, opacity=stroke_o)

    def as_dict(self) -> dict:
        style_dict = {}
        style_dict["fill"] = self.fillcolor.as_hex()
        style_dict["fill-opacity"] = str(self.fillcolor.opacity)
        style_dict["stroke"] = self.linecolor.as_hex()
        style_dict["stroke-opacity"] = str(self.linecolor.opacity)
        return style_dict

    def copy(self):
        return deepcopy(self)


class Drawable:
    def __init__(
        self,
        canvas: Pair,
        elem_id: Optional[str],
        style: DrawableStyle,
    ):
        # ensure canvas can be unpacked
        # throws error if not unpackable
        _, _ = canvas

        self.elem_id = elem_id
        self.canvas_size = canvas

        self.style = style

    def __str__(self):
        name = self.elem_id if self.elem_id else "unnamed"
        return "drawable <{}>".format(name)

    def copy(self):
        return deepcopy(self)

    def get_transform(self, out_bbox: BBox):
        """ Get transforms from bounding box """
        scale_y = out_bbox.height / self.canvas_size[1]
        scale_x = out_bbox.width / self.canvas_size[0]
        return Transform(out_bbox.offset, (scale_x, scale_y))

    def draw(self, surface: RenderSurface, transform=Transform()):
        """ Handle drawing on surface (abstract) """
        pass


class DrawablePath(Drawable):
    def __init__(
        self,
        canvas: Pair,
        elem_id: Optional[str],
        style: DrawableStyle,
    ):
        super().__init__(canvas, elem_id, style)

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

        t = 0.1

        while t <= 1:
            c = [(1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3]
            bx = c[0] * p0.x + c[1] * p1.x + c[2] * p2.x + c[3] * p3.x
            by = c[0] * p0.y + c[1] * p1.y + c[2] * p2.y + c[3] * p3.y

            current_path = self.subpaths[-1]
            current_path.append(Point((bx, by)))

            t += 0.1

        self.current_pos = p3

    def closepath(self):
        current_subpath = self.subpaths[-1]
        dest = current_subpath[0]
        current_subpath.append(dest)
        self.current_pos = dest

    def draw(self, surface: RenderSurface, transform=Transform()):
        """
        Draw path on surface
        --------------------
        - surface   (RenderSurface) - surface to draw on
        - transform (Transform)     - transforms to apply while drawing
        """

        fill = surface.cmap(self.style.fillcolor.rgba)
        stroke = surface.cmap(self.style.linecolor.rgba)

        # skip if transparent
        if not fill[-1] and not stroke[-1]:
            print("skipped")
            return

        for path in self.subpaths:
            # apply transforms to points and convert to tuple for drawing
            path_tuple = [tuple(p.transform(transform)) for p in path]

            # skip if very few points
            if len(path_tuple) < 2:
                continue

            # binary transparency
            if fill[-1] and stroke[-1]:
                surface.draw.polygon(path_tuple, fill=fill[:3], outline=stroke[:3])
            elif fill[-1]:
                surface.draw.polygon(path_tuple, fill=fill[:3])
            else:
                surface.draw.polygon(path_tuple, outline=stroke[:3])


# OBJECT STORAGE
# =======================================
class DrawableObjectStore:
    def __init__(self):

        # drawables stored in drawing order
        self._objects = []

        # stored in dict for lookup by id
        # contains objects with id
        self._named = {}

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
        return self._named.get(elem_id)

    def clear(self):
        self._objects.clear()
        self._named.clear()
