# Security

## Threat model

### Defended

- Inputs larger than `max_bytes` are rejected before format dispatch.
- Images whose declared dimensions exceed `max_pixels` are rejected before decompression: PNG checks IHDR before inflating, and PNM checks the header before reading the raster.
- PNG chunks are length-checked, CRC-checked, and inflated with `zlib.decompressobj(..., max_length=...)` so output cannot exceed the expected raw size by more than one byte.
- PNM rasters are length-checked; P5/P6 samples and P2/P3 tokens are checked against `maxval` and grammar rules.
- Unsupported formats raise `DedupeError` with `unsupported_image`; malformed inputs raise `invalid_image`; oversized inputs raise `input_too_large`; oversized images raise `image_too_large`.
- Library `DedupeError.message` is truncated to 200 characters and contains no image bytes beyond included diagnostic text.

### Not defended

- No authentication, authorization, network isolation, sandboxing, or deletion of files.
- Valid images within the configured byte and pixel limits can still consume CPU and memory while decoding and hashing.
- The CLI follows file paths supplied by the file system and may read through file symlinks; it does not sandbox the scanned folder.
- Image metadata, color profiles, and EXIF data are ignored, not sanitized.

## Mitigations

- `max_bytes` defaults to `104_857_600` bytes (100 MiB) and is checked in `load_image` before parsing.
- `max_pixels` defaults to `50_000_000` pixels and is checked against PNG IHDR dimensions before inflate and PNM dimensions before raster parsing.
- PNG inflate output is bounded to `expected_raw_len + 1`; oversize output raises `invalid_image`.
- PNG chunk CRCs are verified, all five filter types are handled, and invalid filter types raise `invalid_image`.
- PNM `maxval` must be 1-255; truncated rasters, wrong sample counts, and samples above `maxval` raise `invalid_image`.
- The package logger is `perceptual_image_dedupe` with a `NullHandler`; the library does not log file contents. The CLI prints skipped relative paths with error codes to stderr and prints duplicate group paths to stdout.

## Out of scope

The library does not perform authentication, authorization, network I/O, filesystem deletion, JPEG/WebP/GIF decoding, rotation or crop invariance, or GPU execution. Callers are responsible for file access and sandboxing.
