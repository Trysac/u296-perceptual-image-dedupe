"""Decoder for PNM P2, P3, P5 and P6 images."""

from __future__ import annotations

from .errors import DedupeError
from .image import GrayImage

# Dimensions and samples of a supported PNM never need more digits than this.
_MAX_INT_DIGITS = 10


def _skip_whitespace_and_comments(data: bytes, pos: int) -> int:
    """Skip whitespace and '#' comments, returning new position at first non-skipped byte."""
    n = len(data)
    while pos < n:
        b = data[pos]
        if b in (0x20, 0x09, 0x0A, 0x0D):
            pos += 1
        elif b == 0x23:  # '#'
            while pos < n and data[pos] not in (0x0A, 0x0D):
                pos += 1
        else:
            break
    return pos


def _read_int(data: bytes, pos: int) -> tuple[int, int]:
    """Read a decimal integer token, returning value and new position after token."""
    start = pos
    n = len(data)
    while pos < n and 0x30 <= data[pos] <= 0x39:
        pos += 1
    if pos == start:
        raise DedupeError("invalid_image", "expected integer in PNM header")
    if pos - start > _MAX_INT_DIGITS:
        raise DedupeError("invalid_image", "PNM header integer is too large")
    value = int(data[start:pos])
    return value, pos


def _parse_sample(token: bytes, maxval: int) -> int:
    """Parse one ASCII PNM sample, rejecting non-digits and values above maxval."""
    if len(token) > _MAX_INT_DIGITS:
        raise DedupeError("invalid_image", "invalid PNM sample")
    for b in token:
        if not 0x30 <= b <= 0x39:
            raise DedupeError("invalid_image", "invalid PNM sample")
    value = int(token)
    if value > maxval:
        raise DedupeError("invalid_image", "PNM sample exceeds maxval")
    return value


def decode_pnm(data: bytes, max_pixels: int) -> GrayImage:
    """Decode a PNM byte string into a :class:`GrayImage`.

    Supports P2, P3, P5, P6 with maxval 1..255. Header comments are allowed.
    """
    if len(data) < 2:
        raise DedupeError("invalid_image", "PNM too short")
    magic = data[:2]
    if magic not in (b"P2", b"P3", b"P5", b"P6"):
        raise DedupeError("unsupported_image", "unsupported PNM variant")

    pos = 2
    pos = _skip_whitespace_and_comments(data, pos)
    width, pos = _read_int(data, pos)
    pos = _skip_whitespace_and_comments(data, pos)
    height, pos = _read_int(data, pos)
    pos = _skip_whitespace_and_comments(data, pos)
    maxval, pos = _read_int(data, pos)

    if maxval < 1 or maxval > 255:
        raise DedupeError("invalid_image", "maxval must be between 1 and 255")
    if width <= 0 or height <= 0:
        raise DedupeError("invalid_image", "invalid PNM dimensions")
    if width * height > max_pixels:
        raise DedupeError("image_too_large", "PNM dimensions exceed configured maximum")

    # After maxval there must be exactly one whitespace character before the raster.
    if pos >= len(data) or data[pos] not in (0x20, 0x09, 0x0A, 0x0D):
        raise DedupeError("invalid_image", "missing whitespace after PNM header")
    raster_start = pos + 1

    def scale(value: int) -> int:
        return (value * 255 + maxval // 2) // maxval

    if magic == b"P5":
        expected = width * height
        raster = data[raster_start : raster_start + expected]
        if len(raster) != expected:
            raise DedupeError("invalid_image", "truncated P5 raster")
        if any(value > maxval for value in raster):
            raise DedupeError("invalid_image", "P5 sample exceeds maxval")
        pixels = bytes(map(scale, raster))
    elif magic == b"P6":
        expected = width * height * 3
        raster = data[raster_start : raster_start + expected]
        if len(raster) != expected:
            raise DedupeError("invalid_image", "truncated P6 raster")
        if any(value > maxval for value in raster):
            raise DedupeError("invalid_image", "P6 sample exceeds maxval")
        rgb_buf = bytearray(width * height)
        for i in range(width * height):
            r = scale(raster[i * 3])
            g = scale(raster[i * 3 + 1])
            b = scale(raster[i * 3 + 2])
            rgb_buf[i] = (299 * r + 587 * g + 114 * b + 500) // 1000
        pixels = bytes(rgb_buf)
    elif magic == b"P2":
        tokens = data[raster_start:].split()
        if len(tokens) != width * height:
            raise DedupeError("invalid_image", "wrong number of P2 samples")
        pixels = bytes(scale(_parse_sample(t, maxval)) for t in tokens)
    else:  # P3
        tokens = data[raster_start:].split()
        if len(tokens) != width * height * 3:
            raise DedupeError("invalid_image", "wrong number of P3 samples")
        samples = [_parse_sample(t, maxval) for t in tokens]
        rgb_buf = bytearray(width * height)
        for i in range(width * height):
            r = scale(samples[i * 3])
            g = scale(samples[i * 3 + 1])
            b = scale(samples[i * 3 + 2])
            rgb_buf[i] = (299 * r + 587 * g + 114 * b + 500) // 1000
        pixels = bytes(rgb_buf)

    return GrayImage(width, height, pixels)
