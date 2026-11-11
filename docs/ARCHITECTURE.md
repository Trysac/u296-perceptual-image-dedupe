# Architecture

## Overview

The package is split into these modules:

1. `image.py` - `GrayImage`, a frozen dataclass with `width`, `height`, and row-major `pixels` bytes; it validates positive dimensions and exact pixel length.
2. `errors.py` - `DedupeError` with a stable `code` and a message truncated to 200 characters.
3. `loader.py` - `load_image` checks `max_bytes`, dispatches PNM/PNG by signature, and calls the bounded decoders.
4. `pnm.py` - decodes P2, P3, P5, and P6 with `maxval` 1-255 and header comments.
5. `png.py` - decodes 8-bit non-interlaced color types 0, 2, 4, and 6 with all five filter types, CRC checks, and bounded inflate.
6. `hash.py` - box-filter resize, `ahash`, `dhash`, `phash`, and `hamming`.
7. `group.py` - a BK-tree over hashes, union-find for single-link grouping, and sorting of groups.
8. `__main__.py` - CLI folder scanning, hash collection, and group printing.
9. `__init__.py` - exports `DedupeError`, `GrayImage`, `find_duplicates`, `hamming`, `image_hash`, and `load_image`.

## Key design decisions

- **No runtime dependencies**: hashing and PNM/PNG decoding are implemented with the Python standard library; PNG inflate uses `zlib` and chunk headers use `struct`.
- **Specified pixel conversion**: RGB and RGBA use BT.601 integer luma `(299 * R + 587 * G + 114 * B + 500) // 1000`; alpha is composited over white first with `(c * a + 255 * (255 - a) + 127) // 255`.
- **Resize**: the box filter maps output pixel `(x, y)` to the mean of source pixels in the floor-divided source range, with at least one source pixel per output cell.
- **Hashing**: `ahash` uses an 8x8 mean threshold; `dhash` uses 9x8 right-vs-left comparisons; `phash` uses a 32x32 DCT-II, the top-left 8x8 block, and a median threshold excluding DC while still emitting the DC bit. Bits are row-major with the first bit most significant.
- **Determinism**: resize arithmetic uses integer floor divisions. `phash` uses Python floats and `math.cos`; the code does not claim bit-identical results across different Python builds.
- **Limits**: `load_image` checks `max_bytes`; PNG checks IHDR dimensions against `max_pixels` before inflate; zlib output is capped with `max_length`; PNM checks dimensions before raster parsing.
- **Grouping**: the BK-tree prunes candidate pairs by Hamming distance, then union-find produces single-link groups identical to an all-pairs check. Identical hashes are collapsed once per node. Groups contain at least two members, members are sorted, and groups are sorted by first member.

## Error handling

All library-specific failures raise `DedupeError` with a code from `input_too_large`, `image_too_large`, `invalid_image`, `unsupported_image`, `too_many_images`, or `invalid_argument`. Messages are truncated to 200 characters. The CLI catches `DedupeError` and `OSError`, reports skipped files, and returns 2 for usage or missing-folder errors.

## Logging

The package logger is `perceptual_image_dedupe` and has a `NullHandler` by default. The library does not configure logging; the CLI uses `print` for output and error reporting.
