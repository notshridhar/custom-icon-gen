import os
import sys
import shutil
import platform
import argparse

from iconpaths import mac_packages


if platform.system() not in ["Darwin"]:
    exit("this platform is not supported")


parser = argparse.ArgumentParser("icon-recovery")
parser.add_argument("command", choices=["backup", "restore", "cleanup"])
parser.add_argument("--overwrite", action="store_true", help="overwrite mode")
parser.add_argument("--dry-run", action="store_true", help="preview changed")
args = parser.parse_args()


if args.command == "backup":

    if platform.system() == "Darwin":
        for i, pack_info in enumerate(mac_packages.items()):
            pack_name, icon_name = pack_info[0].split(":")
            src_dir = f"/Applications/{pack_name}.app/Contents/Resources"
            dst_dir = f"./backup/{pack_name}"
            src_path = f"{src_dir}/{icon_name}.icns"
            dst_path = f"{dst_dir}/{icon_name}.icns"
            src_exists = os.path.isfile(src_path)
            dst_exists = os.path.isfile(dst_path)
            if src_exists:
                icon_str = f"{pack_name}/{icon_name}.icns"
                print(icon_str, " " * (30 - len(icon_str)), end=" ")
                if not dst_exists or args.overwrite:
                    if not args.dry_run:
                        os.makedirs(dst_dir, exist_ok=True)
                        shutil.copy(src_path, dst_path)
                    print("...copied")
                else:
                    print("...skipped")

            prog = int((i + 1) * 20 / len(mac_packages))
            prog_bar = "=" * prog + " " * (20 - prog)
            print(f"[{prog_bar}] {prog*5}%", end="\r")

elif args.command == "restore":

    # backup folder missing - error
    if not os.path.isdir("./backup"):
        exit("error: backup folder does not exist")

    # check permission and confirmation
    if not args.dry_run:
        if os.geteuid() != 0:
            print("You need to have root privileges to run this script")
            exit("Please try again using sudo")

        print("this is a non-reversible action")
        c = input("continue? [y/N] ")
        if c.lower() != "y":
            exit("abort.")

    if platform.system() == "Darwin":
        for i, pack_info in enumerate(mac_packages.items()):
            pack_name, icon_name = pack_info[0].split(":")
            src_dir = f"./backup/{pack_name}"
            dst_dir = f"/Applications/{pack_name}.app/Contents/Resources"
            src_path = f"{src_dir}/{icon_name}.icns"
            dst_path = f"{dst_dir}/{icon_name}.icns"
            src_exists = os.path.isfile(src_path)
            dst_exists = os.path.isfile(dst_path)

            if src_exists and dst_exists:
                if not args.dry_run:
                    shutil.copy(icon_path, dest_path)
                icon_str = f"{pack_name}/{icon_name}.icns"
                print(icon_str, " " * (30 - len(icon_str)), "...restored")
            
            prog = int((i + 1) * 20 / len(mac_packages))
            prog_bar = "=" * prog + " " * (20 - prog)
            print(f"[{prog_bar}] {prog*5}%", end="\r")

elif args.command == "cleanup":
    shutil.rmtree("./backup")
