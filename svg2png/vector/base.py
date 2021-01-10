from typing import Union, Tuple


# type hints
Num = Union[int, float]
Pair = Tuple[Num, Num]
IntPair = Tuple[int, int]
FloatPair = Tuple[float, float]


class Transform:
    """
    Coordinate Transforms
    ---------------------
    - translate - x and y offset
    - scale     - x and y multipliers
    """

    def __init__(self, translate: Pair = (0, 0), scale: Pair = (1, 1)):
        self.translate = float(translate[0]), float(translate[1])
        self.scale = float(scale[0]), float(scale[1])


class Point:
    """
    2D Point
    --------
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
