# Drawing Module
# -----------
# Functions and classes for drawing


from typing import Optional, Union
from typing import Tuple, List, Dict, Callable

from copy import deepcopy
from abc import abstractmethod, ABC
from PIL import Image, ImageDraw  # type: ignore

from .base import Point, Transform, BBox
from .colors import Color


# type hints
IntPair = Tuple[int, int]
FloatPair = Tuple[float, float]


# SURFACE
# =======================================
class RenderSurface:
    """
    Wrapper class around PIL.Image
    ------------------------------
    Mode = RGBA
    """

    def __init__(self, size: IntPair):
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

    def save(self, filename: str, final_size: Optional[IntPair] = None):
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
    def __init__(self, attrib: dict = {}):

        self.fillcolor = Color()
        self.linecolor = Color()

        self.update(attrib)

    def update(self, attrib: dict):
        """
        Updates style inplace
        update policy: override [newer first]
        """
        fill = attrib.get("fill", "")
        stroke = attrib.get("stroke", "")
        tot_o = float(attrib.get("opacity", 1))
        fill_o = float(attrib.get("fill-opacity", 1)) * tot_o
        stroke_o = float(attrib.get("stroke-opacity", 1)) * tot_o

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
    def draw(self, surface: RenderSurface, transform=Transform()):
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

    def moveto(self, dest: FloatPair, rel=False):
        dest_pt = (Point(dest) + self.current_pos) if rel else Point(dest)
        self.subpaths.append([dest_pt])
        self.current_pos = dest_pt

    def lineto(self, dest: FloatPair, rel=False):
        dest_pt = (Point(dest) + self.current_pos) if rel else Point(dest)
        current_subpath = self.subpaths[-1]
        current_subpath.append(dest_pt)
        self.current_pos = dest_pt

    def curveto(
        self, handle1: FloatPair, handle2: FloatPair, dest: FloatPair, rel=False
    ):
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
            elif stroke[-1]:
                surface.draw.polygon(path_tuple, outline=stroke[:3])


class DrawableEllipse(Drawable):
    def __init__(self, elem_id: str):
        super().__init__(elem_id)

        self.center = Point((0, 0))
        self.radius = Point((0, 0))

    def set_center(self, center: Union[int, float, tuple] = 0):
        if isinstance(center, tuple):
            c_x, c_y = center
            self.center = Point((c_x, c_y))
        elif isinstance(center, int) or isinstance(center, float):
            c_f = float(center)
            self.center = Point((c_f, c_f))

    def set_radius(self, radius: Union[int, float, tuple] = 0):
        if isinstance(radius, tuple):
            r_x, r_y = radius
            self.center = Point((r_x, r_y))
        elif isinstance(radius, int) or isinstance(radius, float):
            r_f = float(radius)
            self.radius = Point((r_f, r_f))

    def draw(self, surface: RenderSurface, transform=Transform()):
        fill = surface.cmap(self.style.fillcolor.rgba)
        stroke = surface.cmap(self.style.linecolor.rgba)

        t_center = self.center.transform(transform)
        t_radius = self.radius.transform(transform)

        bb_min = list(t_center - t_radius)
        bb_max = list(t_center + t_radius)
        ellipse_bbox = bb_min + bb_max

        if fill[-1] and stroke[-1]:
            surface.draw.ellipse(ellipse_bbox, fill[:3], stroke[:3], width=5)
        elif fill[-1]:
            surface.draw.ellipse(ellipse_bbox, fill=fill[:3], width=5)
        elif stroke[-1]:
            surface.draw.ellipse(ellipse_bbox, outline=stroke[:3], width=5)


# OBJECT STORAGE
# =======================================
class DrawableObjectStore:
    def __init__(self, canvas: IntPair):

        self.canvas_size = canvas

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

    def get_transform(self, out_bbox: BBox) -> Transform:
        scale_y = out_bbox.height / self.canvas_size[1]
        scale_x = out_bbox.width / self.canvas_size[0]
        return Transform(out_bbox.offset, (scale_x, scale_y))

    def draw_all(self, surface: RenderSurface, transform=Transform()):
        for drw in self._objects:
            drw.draw(surface, transform)
