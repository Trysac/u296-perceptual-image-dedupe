# trysac-perceptual-image-dedupe

Find duplicate and near-duplicate images with deterministic perceptual hashes, bounded PNM/PNG decoding, and stable grouping. The package uses only the Python standard library; it does not depend on Pillow or NumPy.

## Installation

```bash
pip install trysac-perceptual-image-dedupe
```

## Usage

```python
from perceptual_image_dedupe import load_image, image_hash, find_duplicates

with open("photo.png", "rb") as f:
    img = load_image(f.read())
h = image_hash(img, "dhash")
groups = find_duplicates({"photo.png": h, "other.png": h}, max_distance=10)
print(groups)
```

Command line:

```bash
perceptual-image-dedupe ./photos --method dhash --recursive
```

## Supported formats

- PNM: P2, P3, P5, P6 (maxval 1-255, comments allowed in the header)
- PNG: 8-bit non-interlaced, color types 0 (gray), 2 (RGB), 4 (gray+alpha), 6 (RGBA), all five filter types, chunk CRC checked, and IHDR dimensions checked against `max_pixels` before inflating.

JPEG, WebP and GIF are out of scope: convert them first.

## Hash methods

- `ahash`: resize to 8x8, bit = 1 if the pixel is greater than the mean of the 64 values.
- `dhash`: resize to 9x8, bit = 1 if the right neighbour is greater than the left pixel.
- `phash`: resize to 32x32, apply a 2-D DCT-II, take the top-left 8x8 block, bit = 1 if a coefficient is greater than the median of those 64 values excluding the DC term; the DC term still contributes its own bit.

## Public API

- `GrayImage(width: int, height: int, pixels: bytes)` is a frozen dataclass; `pixels` is row-major with one byte per pixel and length `width * height`. It raises `ValueError` for non-positive dimensions or a wrong pixel length.
- `load_image(data: bytes, *, max_bytes: int = 104_857_600, max_pixels: int = 50_000_000) -> GrayImage` decodes PNM or PNG. It raises `DedupeError` with `input_too_large`, `image_too_large`, `invalid_image`, or `unsupported_image`.
- `image_hash(img: GrayImage, method: Literal["ahash", "dhash", "phash"] = "dhash") -> int` returns a 64-bit hash; an unknown method raises `DedupeError` with `invalid_argument`.
- `hamming(a: int, b: int) -> int` returns the number of differing bits.
- `find_duplicates(hashes: Mapping[str, int], *, max_distance: int = 10, max_items: int = 100_000) -> list[list[str]]` returns single-link groups of size at least two, sorted inside each group, with groups sorted by their first key. A negative `max_distance` raises `invalid_argument`; more than `max_items` hashes raises `too_many_images`.
- `DedupeError(Exception)` exposes `code` and `message`; `message` is truncated to 200 characters. Codes are `input_too_large`, `image_too_large`, `invalid_image`, `unsupported_image`, `too_many_images`, and `invalid_argument`.

The package logger is `perceptual_image_dedupe` and has a `NullHandler` by default. The CLI reads `.png`, `.pgm`, `.ppm`, and `.pnm` files, reports other files as skipped, prints one group per line with paths relative to the folder, exits 0 when no duplicates are found, 1 when duplicates are found, and 2 for usage or a missing folder.

## Why not imagehash

The specification names `imagehash` as the best-known alternative. This package avoids Pillow and NumPy and specifies resizing, grayscale/alpha conversion, hash bit order and grouping so the pipeline is stable across versions.

## Security

The decoding limits and threat model are documented in [docs/SECURITY.md](docs/SECURITY.md).

## Documentation

See `docs/` for architecture, security, testing and project scope.
