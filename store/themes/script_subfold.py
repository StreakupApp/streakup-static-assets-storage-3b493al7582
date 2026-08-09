#!/usr/bin/env python3
"""
Recursively crops exactly 126 pixels off the BOTTOM of every image
found in the script's own folder and all of its subfolders (all x,
last 126 rows of y removed). Overwrites files in place.

Usage (run it from anywhere, it works off its own location):
    python3 crop_bottom.py
    python3 crop_bottom.py --pixels 100        # custom amount
    python3 crop_bottom.py --root /some/path   # walk a different folder instead

Requires: pip install pillow --break-system-packages
"""

import argparse
from pathlib import Path

from PIL import Image

EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

SCRIPT_DIR = Path(__file__).resolve().parent


def crop_bottom_recursive(root: Path, pixels: int) -> None:
    if not root.is_dir():
        raise SystemExit(f"Not a folder: {root}")

    # rglob walks the root and every subfolder beneath it
    images = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSIONS and p != Path(__file__).resolve()
    )

    if not images:
        print(f"No images found under {root}")
        return

    done, skipped = 0, 0
    for path in images:
        try:
            with Image.open(path) as img:
                w, h = img.size
                if h <= pixels:
                    print(f"Skipping {path.relative_to(root)}: height {h}px <= {pixels}px crop")
                    skipped += 1
                    continue

                cropped = img.crop((0, 0, w, h - pixels))
                if path.suffix.lower() in (".jpg", ".jpeg") and cropped.mode in ("RGBA", "P"):
                    cropped = cropped.convert("RGB")
                cropped.save(path)
                print(f"Cropped {path.relative_to(root)}: {w}x{h} -> {w}x{h - pixels}")
                done += 1
        except Exception as e:
            print(f"Failed on {path.relative_to(root)}: {e}")
            skipped += 1

    print(f"\nDone. {done} cropped, {skipped} skipped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively crop the bottom N pixels off every image under a folder (default: the script's own folder)."
    )
    parser.add_argument("--root", type=Path, default=SCRIPT_DIR,
                         help="Folder to walk (default: the folder this script is in)")
    parser.add_argument("--pixels", type=int, default=126,
                         help="Pixels to remove from the bottom (default: 126)")
    args = parser.parse_args()

    crop_bottom_recursive(args.root, args.pixels)
