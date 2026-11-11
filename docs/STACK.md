# Stack

## Used

| Tool | Why |
|---|---|
| Python >= 3.10 | The specification target; the code uses modern typing such as `list[str] | None` and `from __future__ import annotations`. |
| Python standard library | Runtime imports include `argparse`, `os`, `sys`, `logging`, `dataclasses`, `math`, `struct`, `zlib`, `typing`, and `collections.abc`; `allowed_dependencies` is empty. |
| No third-party runtime dependencies | PNG/PNM decoding, resizing, hash methods, Hamming distance, and grouping are implemented in `perceptual_image_dedupe`. |

## Discarded

| Tool | Why not |
|---|---|
| Pillow | Not used; the package implements bounded PNM and PNG decoding itself. |
| NumPy | Not used; hashing and grouping are pure Python. |
| JPEG, WebP, GIF decoders | Out of scope; the README requires converting these formats first. |
| GPU execution and rotation/crop invariance | Out of scope per the specification. |
| File deletion | Out of scope; the CLI only reads files and reports groups. |
