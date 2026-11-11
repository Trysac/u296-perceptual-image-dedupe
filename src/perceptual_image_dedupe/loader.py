"""Top-level image loading and format dispatch."""

from __future__ import annotations

from .errors import DedupeError
from .image import GrayImage
from .png import decode_png
from .pnm import decode_pnm

_DEFAULT_MAX_BYTES = 104_857_600
_DEFAULT_MAX_PIXELS = 50_000_000


def load_image(
    data: bytes,
    *,
    max_bytes: int = _DEFAULT_MAX_BYTES,
    max_pixels: int = _DEFAULT_MAX_PIXELS,
) -> GrayImage:
    """Decode ``data`` as a PNM or PNG image, returning a :class:`GrayImage`.

    Raises:
        DedupeError: with appropriate code if input is too large, image is too
            large, format is unsupported, or data is invalid.
    """
    if len(data) > max_bytes:
        raise DedupeError("input_too_large", "input exceeds maximum byte size")
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return decode_png(data, max_pixels)
    if len(data) >= 2 and data[:2] in (b"P2", b"P3", b"P5", b"P6"):
        return decode_pnm(data, max_pixels)
    raise DedupeError("unsupported_image", "unsupported image format")
