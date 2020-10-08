import os
import shutil
import platform
import argparse
import subprocess

from icongen import iconpaths
from icongen import minimal_round


# check platform
if platform.system() not in ["Darwin"]:
    exit("this platform is not supported")


parser = argparse.ArgumentParser("icongen")
parser.add_argument("--replace", action="store_true", help="replace system files [sudo]")
args = parser.parse_args()


# check permission
if args.replace and os.geteuid() != 0:
    print("You need to have root privileges to run this script")
    exit("Please try again using sudo")


def darwin_check_backup():
    """
    Check if all icons are backed up
    --------------------------------
    Returns if backed up or prompt is overriden
    Exits if not backed up
    """

    # check if all icons are backed up
    not_backed = 0
    for i, pack_info in enumerate(iconpaths.darwin_packages.items()):
        src_path = iconpaths.darwin_decode_path(pack_info[0])
        back_name = "backup_" + src_path.split("/")[-1]
        back_path = "/".join(src_path.split("/")[:-1]) + "/" + back_name

        if os.path.exists(src_path) and not os.path.exists(back_path):
            not_backed += 1

    # backup reminder / confirmation
    if not_backed:
        print(not_backed, "icons are not backed up ...")
        print("this operation will replace original icons")
        print("use recovery tool to backup and restore icons")
        c = input("do you want to continue anyways? [y/N] ")
        if c.lower() != "y":
            exit("abort.")
    else:
        print("this operation will replace original icons")
        c = input("do you want to continue? [y/N] ")
        if c.lower() != "y":
            exit("abort.")
        print("-" * 30)


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
    os.makedirs(outimg, exist_ok=True)
    os.makedirs(outico, exist_ok=True)

    for i, pack_meta in enumerate(iconpaths.darwin_packages.items()):
        
        pack_info, svg_name = pack_meta
        dest_path = iconpaths.darwin_decode_path(pack_info)

        # skip if destination path doesnt exist
        if not os.path.exists(dest_path):
            continue

        svg_path = f"./icons/svg/{svg_name}.svg"
        png_path = f"{outimg}/{svg_name}.png"
        icn_path = f"{outico}/{svg_name}.icns"
        
        # render highest res image
        image = minimal_round.render_from_svg(svg_path, (1024, 1024))
        image.save(png_path, (512, 512))

        # create icns file from png
        darwin_create_icns(png_path, icn_path)
        
        # replace icns
        if args.replace:
            shutil.move(icn_path, dest_path)
        
        # progress bar
        print(pack_info, " "* (30 - len(pack_info)))
        prog = int((i + 1) * 20 / len(iconpaths.darwin_packages))
        prog_bar = "=" * prog + " " * (20 - prog)
        print(f"[{prog_bar}] {prog*5}%", end="\r")
    
    shutil.rmtree(outico, ignore_errors=True)


if platform.system() == "Darwin":
    darwin_generate_all()
    
