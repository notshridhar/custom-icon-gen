import os
import shutil
import platform
import argparse
import subprocess

from iconpaths import mac_packages
from icongen import minimal_round


# check platform
if platform.system() not in ["Darwin"]:
    exit("this platform is not supported")


parser = argparse.ArgumentParser("icongen")
args = parser.parse_args()


# check permission
if os.geteuid() != 0:
    print("You need to have root privileges to run this script")
    exit("Please try again using sudo")


# check if all icons are backed up
not_backed = 0
for pack_info, _ in mac_packages.items():
    pack_name, icon_name = pack_info.split(":")
    back_path = f"./backup/{pack_name}/{icon_name}.icns"
    orig_path = f"/Applications/{pack_name}.app"
    if os.path.isdir(orig_path) and not os.path.isfile(back_path):
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


if platform.system() == "Darwin":

    # output dir configuration
    svgfol = f"./icons/svg"
    outfol = f"./output"
    outimg = f"{outfol}/png"
    outico = f"{outfol}/icns"

    os.makedirs(outfol, exist_ok=True)
    os.makedirs(outimg, exist_ok=True)
    os.makedirs(outico, exist_ok=True)

    for i, pack_meta in enumerate(mac_packages.items()):
        pack_info, svg_name = pack_meta
        pack_name, dst_icon = pack_info.split(":")
        png_path = f"{outimg}/{svg_name}.png"
        ico_path = f"{outico}/{svg_name}.iconset"
        icn_path = f"{outico}/{svg_name}.icns"
        svg_path = f"{svgfol}/{svg_name}.svg"
        dst_path = f"/Applications/{pack_name}.app/Contents/Resources/{dst_icon}.icns"

        # skip if destination package does not exists
        if not os.path.isfile(dst_path):
            continue

        # render highest res image
        image = minimal_round.render_from_svg(svg_path, (1024, 1024))
        image.save(png_path, (512, 512))

        # create iconset folder
        if os.path.exists(ico_path):
            shutil.rmtree(ico_path)
        os.makedirs(ico_path)

        # resize to different resolutions
        sips_cmd = f"sips -z <r1> {png_path} --out {ico_path}/icon_<r2>.png"
        for res in [16, 32, 128, 256]:
            # 1x res
            command = sips_cmd.replace("<r1>", f"{res} {res}")
            command = command.replace("<r2>", f"{res}x{res}")
            subprocess.call(command.split(), stdout=subprocess.DEVNULL)
            # 2x res
            command = sips_cmd.replace("<r1>", f"{res*2} {res*2}")
            command = command.replace("<r2>", f"{res}x{res}@2x")
            subprocess.call(command.split(), stdout=subprocess.DEVNULL)

        # create icns file
        iconutil_cmd = f"iconutil -c icns {ico_path}"
        subprocess.call(iconutil_cmd.split(), stdout=subprocess.DEVNULL)
        assert os.path.exists(icn_path), "icns not created"

        # move icns to source
        shutil.move(icn_path, dst_path)
        output_str = pack_name + ":" + dst_icon
        print(output_str, " "* (30 - len(output_str)))

        # progress bar
        prog = int((i + 1) * 20 / len(mac_packages))
        prog_bar = "=" * prog + " " * (20 - prog)
        print(f"[{prog_bar}] {prog*5}%", end="\r")

        # cleanup iconset
        shutil.rmtree(ico_path, ignore_errors=True)
    
    shutil.rmtree(outico, ignore_errors=True)