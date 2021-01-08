# Parser Module
# -----------------
# Contains tools for parsing svg files
# Limited tag support


from typing import Optional, Union
from typing import Tuple, List, Iterable, Any

from copy import deepcopy
import xml.etree.ElementTree as elemtree
import re

from . import vector


# type hints
Element = elemtree.Element
FloatPair = Tuple[float, float]


# UTILS
# =================
def pair_coords(coord_list: List[float]) -> List[FloatPair]:
    return list(zip(coord_list[::2], coord_list[1::2]))


# SUBPARSERS
# =================
def parse_coords(coord_str: str) -> List[float]:
    """
    Parse 2D coordinate string
    --------------------------
    - Returns list of floats on success
    """

    # regular pattern for parsing numbers
    num_re = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    point_list = list(map(float, re.findall(num_re, coord_str)))
    return point_list


def parse_svg_path(command_str: str, path: vector.DrawablePath):
    """
    Parse svg <path> command string
    Traverse using DrawablePath inbuilt commands
    """

    # temp storages
    command = ""
    argument = ""

    # adding a semicolon as string end marker
    # helps register last command before loop is over
    command_str += ";"

    # supported commands
    supported_commands = set("MZ;LHV;C")

    # parse each char one by one
    for char in command_str:

        # CHAD command
        # ------------------
        # - register previous command + argument
        # - reset prev args and setup next
        if char.upper() in supported_commands:

            command_upper = command.upper()

            # no registered command -> skip
            if not command:
                pass

            # path utils
            # ---------------------
            elif command_upper == "M":
                coord_list = parse_coords(argument)
                dest = pair_coords(coord_list)[0]
                path.moveto(dest, rel=command.islower())

            elif command_upper == "Z":
                path.closepath()

            # straight lines
            # ---------------------
            elif command_upper == "L":
                coord_list = parse_coords(argument)
                dest = pair_coords(coord_list)[0]
                path.lineto(dest, rel=command.islower())

            elif command_upper == "H":
                coord_list = parse_coords(argument)
                dest_x = coord_list[0]
                dest_x -= path.current_pos[0] if command.isupper() else 0
                path.lineto((dest_x, 0), rel=True)

            elif command_upper == "V":
                coord_list = parse_coords(argument)
                dest_y = coord_list[0]
                dest_y -= path.current_pos[1] if command.isupper() else 0
                path.lineto((0, dest_y), rel=True)

            # bezier curves
            # ---------------------
            elif command_upper == "C":
                coord_list = parse_coords(argument)
                h1, h2, dest = pair_coords(coord_list)
                path.curveto(h1, h2, dest, rel=command.islower())

            # end
            # ---------------------
            else:
                print(f"{command} command not supported")

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
class TreeIter:
    def __init__(self, root: Element):
        self.root = root

        self.iter_stack: List[tuple] = []
        self.iter_start = False

    def clean_tag(self, tag: str) -> str:
        """ Get the tag name without namespace """
        pattern = "{.*}\s*"
        return re.sub(pattern, "", tag)

    def __iter__(self):
        self.iter_start = True
        self.root.tag = self.clean_tag(self.root.tag)
        self.iter_stack = [(self.root, self.root[::-1])]
        return self

    def __next__(self):

        # first time iter stack init
        if self.iter_start:
            self.iter_start = False
            return self.root, "entry"

        # continue
        while self.iter_stack:
            top_elem, children = self.iter_stack[-1]

            # child exists -> pop and go to next level
            if children:
                child = children.pop()
                child.tag = self.clean_tag(child.tag)
                self.iter_stack.append((child, child[::-1]))
                return child, "entry"

            # done -> go backwards
            else:
                parent, _ = self.iter_stack.pop()
                return parent, "exit"

        raise StopIteration

    def skip(self):
        """
        Skip all children of last element (recursive)
        ---------------------------------------------
        used when an element handles children itself
        also skips exit event for last event
        note: cannot skip root <svg>
        """
        len_now = len(self.iter_stack)
        while len(self.iter_stack) >= len_now:
            next(self)


class ElemProp:
    def __init__(self, attribs: dict):
        # flags
        self.define_mode = False

        # style
        self.style = vector.DrawableStyle(attribs)

    def copy(self) -> "ElemProp":
        return deepcopy(self)


def get_svg_root(filename: str) -> Element:
    """
    Get root svg element from filename
    Checks version support and validity
    """
    supported_svg_vers = ["1.1"]

    tree = elemtree.parse(filename)
    root = tree.getroot()
    svgver = root.attrib.get("version", "")

    # preliminary check
    if not root.tag.endswith("svg"):
        raise ValueError(f"file {filename} is not a valid svg file")

    # warn if svg version is not tested
    if not svgver:
        print(f"warning: svg version not mentioned")
    elif svgver not in supported_svg_vers:
        print(f"warning: svg version {svgver} is not tested")

    return root


def svg_drawable_handler(elem: Element, prop: ElemProp) -> vector.Drawable:
    """
    Handle drawable elements
    Create drawable from element and attribs
    """

    drw: Any = None
    elem_id = elem.attrib.get("id", "")
    prop.style.update(elem.attrib)

    # <path>
    # parse path and store to render list
    if elem.tag == "path":
        drw = vector.DrawablePath(elem_id)
        drw.style = prop.style.copy()
        parse_svg_path(elem.attrib["d"], drw)

    return drw


def parse_svg_file(filename: str) -> vector.DrawableObjectStore:

    root = get_svg_root(filename)
    namespace = re.findall(r"{.*}\s*", root.tag)[0].strip("{}")

    viewbox = root.attrib.get("viewBox", "").split()

    view_w, view_h = map(int, viewbox[2:])
    canvas_size = (view_w, view_h)

    # state storage
    prop_stack: List[ElemProp] = []
    draw_store = vector.DrawableObjectStore(canvas_size)

    # tag list
    grouping_tags = ["svg", "defs", "g"]
    drawable_tags = ["path"]

    # depth first tree iterator
    iterator = TreeIter(root)
    for elem, event in iterator:

        # exit event -> pop props
        if event == "exit":
            prop_stack.pop()
            continue

        # grouping elements
        # change state for children to inherit
        if elem.tag in grouping_tags:

            if elem.tag == "svg":
                new_prop = ElemProp(elem.attrib)
                prop_stack.append(new_prop)

            elif elem.tag == "defs":
                new_prop = prop_stack[-1].copy()
                new_prop.define_mode = True
                prop_stack.append(new_prop)

            elif elem.tag == "g":
                new_prop = prop_stack[-1].copy()
                new_prop.style.update(elem.attrib)
                prop_stack.append(new_prop)

        # drawables
        # do not change states
        elif elem.tag in drawable_tags:

            # skip all children (recursive)
            iterator.skip()

            # get drawable element after updating props
            prop = prop_stack[-1].copy()
            drw = svg_drawable_handler(elem, prop)

            # append to draw store
            render = not prop.define_mode
            draw_store.append(drw.elem_id, drw, render=render)

        # tag an already defined vector and push it to render list
        # fails if there is no matching id
        elif elem.tag == "use":

            # skip exit event
            iterator.skip()

            # href to id linking
            href_finder = lambda x: x.endswith("href")
            href_key = list(filter(href_finder, elem.attrib))[0]
            href_id = elem.attrib[href_key].lstrip("#")

            # update property
            prop = prop_stack[-1].copy()
            prop.style.update(elem.attrib)

            # get reference as copy
            drw = draw_store.get(href_id).copy()
            drw.elem_id = elem.attrib.get("id", "")
            drw.style.update(prop.style.as_dict())

            # append to draw store
            render = not prop.define_mode
            draw_store.append(drw.elem_id, drw, render=render)

        # fallback
        else:
            iterator.skip()

    return draw_store
