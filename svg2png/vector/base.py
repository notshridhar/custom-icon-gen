from typing import Union, Sequence, Tuple


# type hints
Num = Union[int, float]
Pair = Tuple[Num, Num]
IntPair = Tuple[int, int]
FloatPair = Tuple[float, float]


class Transform:
    """
    Coordinate Transforms
    ---------------------
    - translate (tuple) - x and y offset
    - scale     (tuple) - x and y multipliers
    """

    def __init__(self, translate: Pair = (0, 0), scale: Pair = (1, 1)):

        # unpack and pack for runtime checking
        t_x, t_y = map(float, translate)
        s_x, s_y = map(float, scale)

        self.translate = (t_x, t_y)
        self.scale = (s_x, s_y)


class Point:
    """
    2D Point
    ----------
    - cartesian coordinate system
    - overloaded coordinate arithmetic (+, -)
    - transformable (translate, scale)
    - iterable - can be cast to tuple or list
    - indexable (view only)
    """

    def __init__(self, coord: Pair):
        self.x, self.y = map(float, coord)

    def __getitem__(self, key):
        return [self.x, self.y][key]

    def __iter__(self):
        return iter((self.x, self.y))

    def __add__(self, other):
        return Point((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        return Point((self.x - other.x, self.y - other.y))

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __radd__(self, other):
        return self.__add__(other)

    def __eq__(self, other):
        # works on any unpackable sequence
        o_x, o_y = other
        return self.x == o_x and self.y == o_y

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f})"

    def transform(self, trans: Transform) -> "Point":
        """ Returns copy of point with transforms applied """
        new_x = self.x * trans.scale[0] + trans.translate[0]
        new_y = self.y * trans.scale[1] + trans.translate[1]
        return Point((new_x, new_y))


class BBox:
    """
    Bounding Box
    ------------
    - box - left, top, width, height
    - iterable - can be cast to tuple or list
    - indexable (view only)
    """

    def __init__(self, box: tuple):

        arglist = list(map(float, box))  # type: ignore

        # all params specified
        if len(arglist) == 4:
            self.left, self.top, self.width, self.height = arglist

        # only size specified
        elif len(arglist) == 2:
            self.left, self.top = 0.0, 0.0
            self.width, self.height = arglist

        # invalid
        else:
            raise ValueError("invalid bbox tuple")

    def __getitem__(self, key):
        return [self.left, self.top, self.width, self.height][key]

    def __iter__(self):
        return iter((self.left, self.top, self.width, self.height))

    @property
    def offset(self) -> FloatPair:
        return (self.left, self.top)

    @property
    def size(self) -> FloatPair:
        return (self.width, self.height)

    @property
    def center(self) -> FloatPair:
        hcenter = self.left + self.width / 2
        vcenter = self.top + self.height / 2
        return (hcenter, vcenter)

    def get_sub_bbox(self, fraction: FloatPair, alignment="MM") -> "BBox":
        """
        Get a smaller bounding box from this box
        -------------
        - fraction  (tuple)  - the fraction of box occupied by sub bbox
        - alignment (string) - alignment of sub bbox (horiz, vert)
        """

        # illegal fraction
        if fraction[0] > 1 or fraction[1] > 1:
            raise ValueError("fractions should be strictly <= 1.0")

        # create smaller bbox
        new_width = self.width * fraction[0]
        new_height = self.height * fraction[1]
        smaller = BBox((new_width, new_height))

        # unpack (strictly 2 values)
        halign, valign = tuple(alignment.upper())

        # table for alignment
        htable = {"L": 0, "M": 0.5, "R": 1}
        vtable = {"T": 0, "M": 0.5, "B": 1}

        # align the smaller bbox
        smaller.left = self.left + (self.width - smaller.width) * htable[halign]
        smaller.top = self.top + (self.height - smaller.height) * vtable[valign]

        return smaller
