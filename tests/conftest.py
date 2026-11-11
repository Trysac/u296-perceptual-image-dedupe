"""Shared test helpers for generating deterministic images."""

from __future__ import annotations

import struct
import zlib


def make_png(
    width: int,
    height: int,
    color_type: int,
    raw_pixel_data: bytes,
    filter_type: int = 0,
) -> bytes:
    """Create a minimal valid PNG with a single IDAT, applying the given filter to each row."""
    sig = b"\x89PNG\r\n\x1a\n"
    bpp = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    stride = width * bpp
    raw = bytearray()
    for y in range(height):
        raw.append(filter_type)
        row = raw_pixel_data[y * stride : (y + 1) * stride]
        filtered = bytearray(stride)
        prev_row = (
            raw_pixel_data[(y - 1) * stride : (y - 1) * stride + stride] if y > 0 else bytes(stride)
        )
        for i in range(stride):
            left = row[i - bpp] if i >= bpp else 0
            up = prev_row[i]
            up_left = prev_row[i - bpp] if i >= bpp else 0
            if filter_type == 0:
                pred = 0
            elif filter_type == 1:
                pred = left
            elif filter_type == 2:
                pred = up
            elif filter_type == 3:
                pred = (left + up) // 2
            elif filter_type == 4:
                p = left + up - up_left
                pa = abs(p - left)
                pb = abs(p - up)
                pc = abs(p - up_left)
                pred = left if pa <= pb and pa <= pc else up if pb <= pc else up_left
            else:
                raise ValueError
            filtered[i] = (row[i] - pred) & 0xFF
        raw.extend(filtered)
    compressed = zlib.compress(bytes(raw))

    def chunk(ctype: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + ctype
            + data
            + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(
        ">IIBBBBB",
        width,
        height,
        8,
        color_type,
        0,
        0,
        0,
    )
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
