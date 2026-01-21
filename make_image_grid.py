#!/usr/bin/env python3
import argparse
import math
import os
from pathlib import Path

from PIL import Image


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff", ".webp"}


def iter_images(folder: Path):
    for entry in sorted(folder.iterdir()):
        if entry.is_file() and entry.suffix.lower() in IMAGE_EXTS:
            yield entry


def load_and_fit(path: Path, cell_w: int, cell_h: int, bg_color):
    with Image.open(path) as im:
        im = im.convert("RGBA")
        scale = min(cell_w / im.width, cell_h / im.height)
        new_w = max(1, int(im.width * scale))
        new_h = max(1, int(im.height * scale))
        im = im.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGBA", (cell_w, cell_h), bg_color)
        off_x = (cell_w - new_w) // 2
        off_y = (cell_h - new_h) // 2
        canvas.paste(im, (off_x, off_y), im)
        return canvas.convert("RGB")


def main():
    parser = argparse.ArgumentParser(
        description="Create a single image grid from all images in a folder."
    )
    parser.add_argument("folder", help="Folder containing images")
    parser.add_argument(
        "-o",
        "--output",
        default="grid.jpg",
        help="Output image file path (default: grid.jpg)",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=0,
        help="Number of columns (default: auto)",
    )
    parser.add_argument(
        "--cell-width",
        type=int,
        default=0,
        help="Cell width in pixels (default: max image width)",
    )
    parser.add_argument(
        "--cell-height",
        type=int,
        default=0,
        help="Cell height in pixels (default: max image height)",
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=8,
        help="Padding between cells in pixels (default: 8)",
    )
    parser.add_argument(
        "--bg",
        default="#ffffff",
        help="Background color (default: #ffffff)",
    )
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}")

    images = list(iter_images(folder))
    if not images:
        raise SystemExit("No images found in the folder.")

    sizes = []
    for p in images:
        with Image.open(p) as im:
            sizes.append(im.size)

    max_w = max(w for w, _ in sizes)
    max_h = max(h for _, h in sizes)
    cell_w = args.cell_width or max_w
    cell_h = args.cell_height or max_h

    cols = args.cols or math.ceil(math.sqrt(len(images)))
    rows = math.ceil(len(images) / cols)

    pad = args.padding
    grid_w = cols * cell_w + (cols - 1) * pad
    grid_h = rows * cell_h + (rows - 1) * pad

    grid = Image.new("RGB", (grid_w, grid_h), args.bg)

    for idx, img_path in enumerate(images):
        r = idx // cols
        c = idx % cols
        x = c * (cell_w + pad)
        y = r * (cell_h + pad)
        cell = load_and_fit(img_path, cell_w, cell_h, args.bg)
        grid.paste(cell, (x, y))

    out_path = Path(args.output)
    grid.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
