# Drawing Module
# -----------
# Module that contains drawing functions and classes


from PIL import Image, ImageDraw

from abc import abstractmethod

from svg2png import utils


# BASIC
# =======================================
class Transform:
    """
    Coordinate Transforms
    ---------------------
    - translate (tuple)
    - scale     (tuple)
    """
    def __init__(self, translate=(0, 0), scale=(1., 1.)):
        self.translate = translate
        self.scale = scale


class BoundingBox:
    """
    Bounding Box
    ------------
    - bbox (tuple) - left, top, width, height
    """
    def __init__(self, bbox: tuple):
        self.left, self.top, self.width, self.height = bbox
    
    def astuple(self):
        return (self.left, self.top, self.width, self.height)

    def get_sub_bbox(self, fraction: tuple, alignment="MM"):
        """
        Get a smaller bounding box from this
        -------------
        - fraction  (tuple | float) - the fraction of box occupied by sub bbox
        - alignment (string)        - alignment of sub bbox (horiz, vert)
        """

        # convert to tuple if single value specified
        if type(fraction) == float:
            fraction = (fraction, fraction)

        # illegal fraction
        if fraction[0] > 1 or fraction[1] > 1:
            raise ValueError("fractions should be strictly <= 1.0")

        # unpack (strictly 2 values)
        horiz_align, vert_align = alignment.upper()
        
        new_width = self.width * fraction[0]
        new_height = self.height * fraction[1]
        smaller = BoundingBox((0, 0, new_width, new_height))

        # horizontal alignment - Left, Mid, Right
        if horiz_align == "L":
            smaller.left = 0
        elif horiz_align == "M":
            smaller.left = (self.width - smaller.width) * 0.5
        elif horiz_align == "R":
            smaller.left = self.width - smaller.width
        else:
            raise ValueError("Invalid horizontal alignment")

        # vertical alignment - Top, Mid, Bottom
        if vert_align == "T":
            smaller.top = 0
        elif vert_align == "M":
            smaller.top = (self.height - smaller.width) * 0.5
        elif vert_align == "B":
            smaller.top = self.height - smaller.width
        else:
            raise ValueError("Invalid vertical alignment")

        return smaller


# DRAWING
# =======================================
class Point:
    """
    2D Point
    ----------
    - cartesian coordinate system
    - basic coordinate arithmetic supported (+, *)
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def as_tuple(self):
        """ Get tuple representation """
        return (self.x, self.y)
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __mul__(self, other):
        return Point(self.x * other.x, self.y * other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    
    def __imul__(self, other):
        self.x *= other.x
        self.y *= other.y
        return self
    
    def transform(self, trans: Transform):
        """ Returns copy of point with transforms applied """
        new_x = self.x * trans.scale[0] + trans.translate[0]
        new_y = self.y * trans.scale[1] + trans.translate[1]
        return Point(new_x, new_y)


class RenderSurface:
    """
    Thin wrapper around PIL.Image
    -----------------------------
    Mode = RGBA
    """

    def __init__(self, size: tuple):
        self.image = Image.new("RGBA", size)
        self.draw = ImageDraw.Draw(self.image)

        # color mapping function (callable)
        self.cmap = lambda x: x

    def set_color_map(self, color_map):
        """
        Set function to generate output color from rules
        This can be simple lambda or complex function with multiple rules
        """
        self.cmap = color_map

    def save(self, filename: str, final_size: tuple = None):
        """
        Save the rendered image with optional anti-aliasing
        If final size is given, saves resized image with antialiasing
        """
        if final_size:
            final = self.image.resize(final_size, resample=Image.ANTIALIAS)
        else:
            final = self.image

        final.save(filename, "PNG")


class Drawable:
    def __init__(self, id: str, canvas: tuple):
        self.id = id
        self.canvas_size = canvas

        # ensure canvas can be unpacked into two
        # throws error if not
        _, _ = canvas

        # attribs ending with "color" will be remapped while drawing
        self.fillcolor = ""
        self.linecolor = ""

    def remap_color(func):
        """
        Decorator for color remapping
        -------------------------------
        changes color only for decorated function
        retains old colors (safe multiple passes)
        """

        def inner(self, surface, *args, **kwargs):

            self_dict = vars(self)
            saved_dict = {}

            # find keys ending with "color"
            color_finder = lambda x: x.endswith("color")
            color_keys = utils.find_dict_keys(self_dict, color_finder)

            # apply map on all colors
            for ckey in color_keys:
                saved_dict[ckey] = self_dict[ckey]
                self_dict[ckey] = surface.cmap(self_dict[ckey])

            # this wont return anything
            func(self, surface, *args, **kwargs)

            # reset old colors
            for ckey in color_keys:
                self_dict[ckey] = saved_dict[ckey]

        return inner

    def get_transform(self, bounding_box: BoundingBox):
        """ Get transforms from bounding box """
        translate= (bounding_box.left, bounding_box.top)
        scale_y = bounding_box.height / self.canvas_size[1]
        scale_x = bounding_box.width / self.canvas_size[0]
        return Transform(translate=translate, scale=(scale_x, scale_y))

    @abstractmethod
    def draw(self, surface: RenderSurface, transform=Transform()):
        """ Handle drawing on surface (abstract) """
        pass


class DrawablePath(Drawable):
    def __init__(self, id: str, canvas: tuple, fill="", outline=""):
        super().__init__(id, canvas)

        self.subpaths = []

        # threshold for creating a curved path
        self.curve_resolution = 1

        # maintain last coordinate
        # easier than getting last list element
        self.current_pos = Point(0, 0)

        self.fillcolor = fill
        self.linecolor = outline
    
    def moveto(self, dest:Point):
        self.subpaths.append([dest])
        self.current_pos = dest
    
    def rmoveto(self, dest:Point):
        self.moveto(dest + self.current_pos)

    def lineto(self, dest:Point):
        current_subpath = self.subpaths[-1]
        current_subpath.append(dest)
        self.current_pos = dest
    
    def rlineto(self, dest:Point):
        self.lineto(dest + self.current_pos)

    def closepath(self):
        current_subpath = self.subpaths[-1]
        dest = current_subpath[0]
        current_subpath.append(dest)
        self.current_pos = dest

    def curveto(self, handle1: Point, handle2: Point, dest: Point):
        p0 = self.current_pos
        p1 = handle1
        p2 = handle2
        p3 = dest

        t = 0.1

        while t <= 1:
            c = [(1-t)**3, 3 * (1-t)**2 * t, 3 * (1-t) * t**2, t**3]
            bx = c[0] * p0.x + c[1] * p1.x + c[2] * p2.x + c[3] * p3.x
            by = c[0] * p0.y + c[1] * p1.y + c[2] * p2.y + c[3] * p3.y

            current_path = self.subpaths[-1]
            current_path.append(Point(bx, by))

            t += 0.1
        
        self.current_pos = dest

    def rcurveto(self, handle1: Point, handle2: Point, dest: Point):
        handle1 += self.current_pos
        handle2 += self.current_pos
        dest += self.current_pos
        self.curveto(handle1, handle2, dest)

    @Drawable.remap_color
    def draw(self, surface: RenderSurface, transform=Transform()):
        """
        Draw path on surface
        --------------------
        - surface   (RenderSurface) - surface to draw on
        - transform (Transform)     - transforms to apply while drawing
        """

        for path in self.subpaths:
            # apply transforms to points and convert to tuple for drawing
            path = [p.transform(transform).as_tuple() for p in path]

            # draw filled polygon
            surface.draw.polygon(path, fill=self.fillcolor, outline=self.linecolor)
