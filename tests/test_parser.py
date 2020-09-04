import unittest

from svg2png import parser
from svg2png import vector


class TestA1_Subparsers(unittest.TestCase):
    def test_a(self):
        # coordinate parser

        # different types
        p = parser.parse_coords("120 200")
        self.assertTrue(p == [120, 200])
        p = parser.parse_coords("12.0,20.0")
        self.assertTrue(p == [12, 20])
        p = parser.parse_coords("12-20")
        self.assertTrue(p == [12, -20])
        p = parser.parse_coords("122e-1, -20")
        self.assertTrue(p == [12.2, -20])
        p = parser.parse_coords("122e-1-20")
        self.assertTrue(p == [12.2, -20])

        # different number of points
        p = parser.parse_coords("12e1")
        self.assertTrue(p == [120])
        p = parser.parse_coords("-12-24,-41")
        self.assertTrue(p == [-12, -24, -41])

    def test_b(self):
        # path parser

        # straight lines
        string = "M2 5 H20 L10 34e-1 V15 Z m2 5 h20 l10-30 v15 z"
        expct1 = [(2, 5), (20, 5), (10, 3.4), (10, 15), (2, 5)]
        expct2 = [(4, 10), (24, 10), (34, -20), (34, -5), (4, 10)]
        path = vector.DrawablePath("path")
        parser.parse_svg_path(string, path)
        self.assertTrue(path.subpaths == [expct1, expct2])


def main():
    unittest.main()


if __name__ == "__main__":
    main()
