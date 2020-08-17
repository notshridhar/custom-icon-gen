# Parser Module
# -----------------
# Contains tools for parsing svg format and other strings


import xml.etree.ElementTree as elemtree
import re

from svg2png import draw
from svg2png import utils


# ERRORS
# ================
def parser_error(message):
    print("ParserError: {}".format(message))


def parser_warning(message):
    print("ParserWarning: {}".format(message))


# COLOR
# =================
def parse_hex_color(color_str: str) -> tuple:
    """
    Parse hex color string to get tuple(R,G,B)
    Returns tuple is success else returns none
    """

    if type(color_str) != str:
        message = "hex color got an input that is not a string"
        parser_error(message)
        return
    
    color_str = color_str.strip("#")

    try:
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
        return (r,g,b)
    except IndexError:
        message = "hex color too short"
        parser_error(message)
        return
    except ValueError:
        message = "invalid hex color"
        parser_error(message)
        return


def create_hex_color(color: tuple) -> str:
    """ Create hex color string from color tuple """
    final_string = ""
    for i in color:
        final_string += hex(int(i)).lower().lstrip("0x")
    return "#" + final_string


# SUBPARSERS
# =================
def parse_svg_coords(coord_str: str, num_coords=1) -> list:
    """
    Parse 2D coordinate string
    --------------------------
    - Assumes space / comma delimited string
    - Returns list of Points on success, none on failure
    """

    # convert to list of floats
    try:
        coord_list = coord_str.replace(",", " ").split()
        coord_list = list(map(float, coord_list))
    except ValueError:
        error_msg = "float casting failure - {}".format(coord_str)
        parser_error(error_msg)
        return

    # expected coordinates mismatch
    if len(coord_list) != num_coords * 2:
        error_msg = "expected {} arguments but {} found"
        parser_error(error_msg.format(num_coords * 2, len(coord_list)))
        return
    
    # convert to list of points
    point_list = [draw.Point(x, y) for x, y in zip(coord_list[0::2], coord_list[1::2])]
    return point_list


def parse_svg_path(command_str: str, path: draw.DrawablePath):
    """
    Parse <path> command string
    --------------------------
    - Creates list of polygons
    - The paths will be closed while drawing

    Supported Commands
    ------------------
    - M / m - MoveTo
    - L / l - LineTo
    - Z / z - ClosePath
    """

    # temp storages
    command = ""
    argument = ""

    # adding a semicolon as string end marker
    # helps register last command before loop is over
    command_str += ";"
    
    # parse each char one by one
    # not at all efficient, but boy is it readable
    for char in command_str:

        # CHAD command
        # ------------------
        # - register previous command + argument
        # - reset prev args and setup next
        # - literally has alpha in condition
        if char.isalpha() or char == ";":

            if not command:
                pass

            elif command.upper() == "M":
                dest = parse_svg_coords(argument, 1)[0]
                path.moveto(dest, rel=command.islower())
            
            elif command.upper() == "L":
                dest = parse_svg_coords(argument, 1)[0]
                path.lineto(dest, rel=command.islower())
            
            elif command.upper() == "Z":
                path.closepath()

            # elif command == "C":
            #     coord_args = parse_svg_coords(argument, 3)
            #     handle1, handle2, dest = coord_args
            #     path.curveto(dest, handle1, handle2)
            
            else:
                error_msg = "{} command not supported".format(command)
                parser_error(error_msg)

            # setup next command
            command = char
            argument = ""

        # VIRGIN argument
        # ------------------
        # - just keep appending to argument
        # - depends on next command to make sense of it
        else:
            argument += char


# SVG PARSER
# =================
class SVGParser:
    """
    Thin wrapper around xml.etree.ElementTree
    Customized for svg parsing
    -----------------------------
    Versions supported: SVG 1.1
    """

    SUPPORTED_VERS = ["1.1"]
    SVG_NS = {"svg": "http://www.w3.org/2000/svg"}

    def __init__(self, filename):
        self.tree = elemtree.parse(filename)

        root = self.tree.getroot()
        attribs = root.attrib

        self.canvas_size = (int(attribs["width"]), int(attribs["height"]))

        # warn if svg version is untested
        if attribs["version"] not in self.SUPPORTED_VERS:
            message = "svg version:{} is experimental".format(svg_ver)
            parser_warning(message)

        # construct style table for id lookup
        self.styles = self._construct_style_table()

    def _construct_style_table(self):
        style_dict = {}

        for elem in self.tree.iter():
            tag_clean = re.sub("{.*}\s*", "", elem.tag)

            if tag_clean == "use":
                
                href_finder = lambda x: x.endswith("href")
                use_key = utils.find_dict_keys(elem.attrib, href_finder)[0]
                use_id = elem.attrib[use_key]

                if use_id not in style_dict:
                    style_dict[use_id] = elem.attrib
                else:
                    style_dict[use_id].update(elem.attrib)

        return style_dict

    def get_drawables(self) -> list:
        """ Get list of drawable objects """
        drawables = []
        defs = self.tree.find("svg:defs", namespaces=SVGParser.SVG_NS)

        for elem in defs:

            elem_id = elem.attrib["id"]
            tag_clean = re.sub("{.*}\s*", "", elem.tag)

            if tag_clean == "path":
                # get style from id
                style = self.styles.get("#" + elem_id, {})
                # create drawable
                path = draw.DrawablePath(
                    id=elem_id,
                    canvas=self.canvas_size,
                    fill=style.get("fill"),
                    outline=style.get("stroke"),
                )
                parse_svg_path(elem.attrib["d"], path)
            else:
                print("tag: {} is not supported yet :(".format(tag_clean))
                continue

            drawables.append(path)

        return drawables
