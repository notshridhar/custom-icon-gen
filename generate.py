import os
import shutil
import platform
import argparse
import subprocess

from icongen import iconpaths
from icongen import minimal_round


# check platform for early fail
if platform.system() not in ["Darwin"]:
    exit("this platform is not supported")


parser = argparse.ArgumentParser("icongen")
parser.add_argument(
    "--replace", action="store_true", help="replace system files [sudo]"
)
args = parser.parse_args()


# check permission
if args.replace and os.geteuid() != 0:
    print("You need to have root privileges to run this script")
    exit("Please try again using sudo")


def darwin_create_icns(png_path: str, icn_path: str):
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


def darwin_generate_all():
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

        dest_path, svg_name = pack_meta

        # skip if destination path doesnt exist
        if not os.path.exists(dest_path):
            continue

        svg_path = f"./icons/svg/{svg_name}.svg"
        png_path = f"{outimg}/{svg_name}.png"
        icn_path = f"{outico}/{svg_name}.icns"

        # render highest res image
        if True or not os.path.isfile(svg_path):
            image = minimal_round.render_from_svg(svg_path, (512, 512))
            image.save(png_path, (256, 256))

        # create and replace icns
        if args.replace:
            darwin_create_icns(png_path, icn_path)
            shutil.move(icn_path, dest_path)

        # progress bar
        print(dest_path, " " * (40 - len(dest_path)))
        prog = int((i + 1) * 20 / len(icon_list))
        prog_bar = "=" * prog + " " * (20 - prog)
        print(f"[{prog_bar}] {prog*5}%", end="\r")

    # remove icns if empty
    try:
        os.rmdir(outico)
    except OSError:
        pass


if platform.system() == "Darwin":
    darwin_generate_all()
