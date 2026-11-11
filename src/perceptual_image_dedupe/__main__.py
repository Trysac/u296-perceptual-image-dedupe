"""Command-line interface: find duplicate images in a folder."""

from __future__ import annotations

import argparse
import os
import sys

from .errors import DedupeError
from .group import find_duplicates
from .hash import image_hash
from .loader import load_image

_SUPPORTED_EXTENSIONS = {".png", ".pgm", ".ppm", ".pnm"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="perceptual-image-dedupe",
        description="Find duplicate and near-duplicate images in a folder.",
    )
    parser.add_argument("folder", help="folder to scan")
    parser.add_argument(
        "--method",
        choices=["ahash", "dhash", "phash"],
        default="dhash",
        help="perceptual hash method (default: dhash)",
    )
    parser.add_argument(
        "--max-distance",
        type=int,
        default=10,
        help="maximum Hamming distance for a duplicate (default: 10)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="recurse into subdirectories",
    )

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2

    folder = args.folder
    if not os.path.isdir(folder):
        print(f"error: folder not found: {folder}", file=sys.stderr)
        return 2

    def iter_files() -> list[tuple[str, str]]:
        result = []
        if args.recursive:
            for root, _, files in os.walk(folder):
                for name in files:
                    full = os.path.join(root, name)
                    rel = os.path.relpath(full, folder)
                    result.append((full, rel))
        else:
            for name in os.listdir(folder):
                full = os.path.join(folder, name)
                if os.path.isfile(full):
                    result.append((full, os.path.relpath(full, folder)))
        return result

    hashes: dict[str, int] = {}
    for full, rel in iter_files():
        ext = os.path.splitext(rel)[1].lower()
        if ext not in _SUPPORTED_EXTENSIONS:
            print(f"skipped: {rel} unsupported_image", file=sys.stderr)
            continue
        try:
            with open(full, "rb") as f:
                data = f.read()
            img = load_image(data)
            hash_val = image_hash(img, args.method)
            hashes[rel] = hash_val
        except DedupeError as e:
            print(f"skipped: {rel} {e.code}", file=sys.stderr)
        except OSError:
            print(f"skipped: {rel} invalid_image", file=sys.stderr)

    try:
        groups = find_duplicates(hashes, max_distance=args.max_distance)
    except DedupeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    for group in groups:
        print(" ".join(group))
    return 1 if groups else 0


if __name__ == "__main__":
    raise SystemExit(main())
