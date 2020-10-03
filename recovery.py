import os
import sys
import shutil
import platform
import argparse

from icongen import iconpaths


if platform.system() not in ["Darwin"]:
    exit("this platform is not supported")


# argument parser
parser = argparse.ArgumentParser("icon-recovery")
parser.add_argument("command", choices=["backup", "restore", "cleanup"])
parser.add_argument("--dry-run", action="store_true", help="preview changed")
args = parser.parse_args()


# check permission and confirmation
if not args.dry_run:
    if os.geteuid() != 0:
        print("You need to have root privileges to run this script")
        exit("Please try again using sudo")
    
    print("this is a non-reversible action")
    c = input("continue? [y/N] ")
    if c.lower() != "y":
        exit("abort.")


if args.command == "backup":
    for i, pack_info in enumerate(iconpaths.darwin_packages.items()):
        src_path = iconpaths.darwin_decode_path(pack_info[0]) 
        back_name = "backup_" + src_path.split("/")[-1]
        dest_path = "/".join(src_path.split("/")[:-1]) + "/" + back_name

        # copy only if src exists
        if os.path.exists(src_path):
            if not args.dry_run:
                shutil.copy(src_path, dest_path)
            print(dest_path, " " * (30 - len(dest_path)), "...copied")

        # progress bar
        prog = int((i + 1) * 20 / len(iconpaths.darwin_packages))
        prog_bar = "=" * prog + " " * (20 - prog)
        print(f"[{prog_bar}] {prog*5}%", end="\r")

elif args.command == "restore":
    for i, pack_info in enumerate(iconpaths.darwin_packages.items()):
        dest_path = iconpaths.darwin_decode_path(pack_info[0])
        back_name = "backup_" + src_path.split("/")[-1]
        src_path = "/".join(dest_path.split("/")[:-1]) + "/" + back_name

        # copy only if src and dest both exist
        if os.path.exists(src_path) and os.path.exists(dest_path):
            if not args.dry_run:
                shutil.copy(src_path, dest_path)
            print(dest_path, " " * (30 - len(dest_path)), "...restored")

        # progress bar
        prog = int((i + 1) * 20 / len(iconpaths.darwin_packages))
        prog_bar = "=" * prog + " " * (20 - prog)
        print(f"[{prog_bar}] {prog*5}%", end="\r")

elif args.command == "cleanup":
    for i, pack_info in enumerate(iconpaths.darwin_packages.items()):
        dest_path = iconpaths.darwin_decode_path(pack_info[0])
        back_name = "backup_" + dest_path.split("/")[-1]
        back_path = "/".join(dest_path.split("/")[:-1]) + "/" + back_name

        # delete only if exists
        if os.path.exists(back_path):
            if not args.dry_run:
                if os.path.isdir(back_path):
                    shutil.rmtree(back_path)
                else:
                    os.remove(back_path)
            print(back_path, " " * (30 - len(back_path)), "...deleted")

        # progress bar
        prog = int((i + 1) * 20 / len(iconpaths.darwin_packages))
        prog_bar = "=" * prog + " " * (20 - prog)
        print(f"[{prog_bar}] {prog*5}%", end="\r")
