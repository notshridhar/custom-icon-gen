from typing import Union, Tuple

# type hints
Number = Union[int, float]
FloatPair = Tuple[float, float]


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
            raise ValueError("invalid bbox constructor")

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

    def get_sub_bbox(
        self, fraction: Union[Number, FloatPair], alignment="MM"
    ) -> "BBox":
        """
        Get a smaller bounding box from this box
        -------------
        - fraction  - the fraction of box occupied by sub bbox
        - alignment - alignment of sub bbox (horiz, vert)
        """
        # convert to tuple if number given
        if isinstance(fraction, float) or isinstance(fraction, int):
            fraction = (fraction, fraction)

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
