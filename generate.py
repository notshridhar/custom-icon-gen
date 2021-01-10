import os
import shutil
import platform
import argparse
import contextlib
import subprocess

from icongen import iconpaths
from icongen import minimal_round


class DarwinGenerator:
    @classmethod
    def create_icns(cls, png_path: str, icn_path: str):
        """
        Create icns file from highres png file
        Throws AssertionError if icns is not created successfully
        """

        # create fresh iconset folder (intermediate)
        iconset_path = ".".join(icn_path.split(".")[:-1]) + ".iconset"
        if os.path.exists(iconset_path):
            shutil.rmtree(iconset_path)
        os.makedirs(iconset_path)

        # resize png to different resolutions using sips
        sips_cmd = f"sips -z <r1> {png_path} --out {iconset_path}/icon_<r2>.png"
        for res in [16, 32, 128, 256]:
            # 1x res
            command = sips_cmd.replace("<r1>", f"{res} {res}")
            command = command.replace("<r2>", f"{res}x{res}")
            subprocess.call(command.split(), stdout=subprocess.DEVNULL)
            # 2x res
            command = sips_cmd.replace("<r1>", f"{res*2} {res*2}")
            command = command.replace("<r2>", f"{res}x{res}@2x")
            subprocess.call(command.split(), stdout=subprocess.DEVNULL)

        # create icns file from iconset
        iconutil_cmd = f"iconutil -c icns {iconset_path}"
        subprocess.call(iconutil_cmd.split(), stdout=subprocess.DEVNULL)
        assert os.path.exists(icn_path), "icns not created"

        # cleanup iconset
        shutil.rmtree(iconset_path)

    @classmethod
    def generate_all(cls, replace=False):
        """ Generate icons and replace original """

        # output dir configuration
        outimg = f"./output/png"
        outico = f"./output/icns"

        # create output dirs
        orig_umask = os.umask(0)
        os.makedirs(outimg, exist_ok=True)
        # os.makedirs(outico, exist_ok=True)
        os.umask(orig_umask)

        icon_list = iconpaths.darwin_get_store()
        for i, pack_meta in enumerate(icon_list):

            dest_path = pack_meta["dest"]
            svg_name = pack_meta["svg"]
            color_scheme = pack_meta["color"]

            # skip if destination path doesnt exist
            if not os.path.exists(dest_path):
                continue

            svg_path = f"./icons/svg/{svg_name}.svg"
            png_path = f"{outimg}/{svg_name}.png"
            icn_path = f"{outico}/{svg_name}.icns"

            # render png image for highest res
            if not os.path.isfile(png_path):
                image = minimal_round.render_svg(svg_path, (512, 512), color_scheme)
                image.save(png_path, "PNG")

            # create and replace icns
            if replace:
                cls.create_icns(png_path, icn_path)
                shutil.move(icn_path, dest_path)

            # progress bar
            print(dest_path, " " * (40 - len(dest_path)))
            prog = int((i + 1) * 20 / len(icon_list))
            prog_bar = "=" * prog + " " * (20 - prog)
            print(f"[{prog_bar}] {prog*5}%", end="\r")

        # remove icns if empty
        with contextlib.suppress(OSError):
            os.rmdir(outico)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("icongen")
    parser.add_argument(
        "--replace", action="store_true", help="replace system files [sudo]"
    )
    return parser.parse_args()


def main():

    SUPPORTED_PLATFORMS = ["Darwin"]

    # check platform for early fail
    if platform.system() not in SUPPORTED_PLATFORMS:
        exit("This platform is not currently supported :(")

    # parse arguments
    args = parse_args()

    # check permission for early fail
    if args.replace and os.geteuid() != 0:
        print("Admin privileges are required to overwrite system files")
        print("Please try running the script with elevated privilege")
        exit()

    # forward to platform specific handler
    DarwinGenerator.generate_all(replace=args.replace)


if __name__ == "__main__":
    main()
