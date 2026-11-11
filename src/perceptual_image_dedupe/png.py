"""Minimal PNG decoder for 8-bit non-interlaced gray/RGB/gray+alpha/RGBA images."""

from __future__ import annotations

import struct
import zlib

from .errors import DedupeError
from .image import GrayImage


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _bytes_per_pixel(color_type: int) -> int:
    return {0: 1, 2: 3, 4: 2, 6: 4}[color_type]


def decode_png(data: bytes, max_pixels: int) -> GrayImage:
    """Decode a PNG byte string into a :class:`GrayImage`.

    Supports color types 0, 2, 4, 6 with bit depth 8, non-interlaced, all filter types.
    """
    signature = b"\x89PNG\r\n\x1a\n"
    if not data.startswith(signature):
        raise DedupeError("unsupported_image", "not a PNG file")

    pos = len(signature)
    width = height = 0
    color_type = -1
    idat = bytearray()
    expected_raw_len = 0

    while pos < len(data):
        if pos + 12 > len(data):
            raise DedupeError("invalid_image", "truncated PNG chunk header")
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        pos += 4
        chunk_type = data[pos : pos + 4]
        pos += 4
        if pos + length + 4 > len(data):
            raise DedupeError("invalid_image", "truncated PNG chunk")
        chunk_data = data[pos : pos + length]
        pos += length
        stored_crc = struct.unpack(">I", data[pos : pos + 4])[0]
        pos += 4
        calc_crc = zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        if stored_crc != calc_crc:
            raise DedupeError("invalid_image", "PNG chunk CRC mismatch")

        if chunk_type == b"IHDR":
            if length != 13:
                raise DedupeError("invalid_image", "invalid IHDR length")
            (
                width,
                height,
                bit_depth,
                color_type,
                compression,
                filter_method,
                interlace,
            ) = struct.unpack(">IIBBBBB", chunk_data)
            if bit_depth != 8 or color_type not in (0, 2, 4, 6):
                raise DedupeError("unsupported_image", "unsupported PNG bit depth or color type")
            if compression != 0 or filter_method != 0 or interlace != 0:
                raise DedupeError(
                    "unsupported_image", "unsupported PNG compression, filter or interlace"
                )
            if width <= 0 or height <= 0:
                raise DedupeError("invalid_image", "invalid PNG dimensions")
            if width * height > max_pixels:
                raise DedupeError("image_too_large", "PNG dimensions exceed configured maximum")
            bpp = _bytes_per_pixel(color_type)
            expected_raw_len = height * (1 + width * bpp)
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break
        # other chunk types are ignored

    if width == 0 or height == 0 or not idat:
        raise DedupeError("invalid_image", "missing IHDR or IDAT")

    decomp = zlib.decompressobj()
    raw = bytearray()
    remaining = bytes(idat)
    while remaining:
        try:
            out = decomp.decompress(remaining, max_length=expected_raw_len + 1 - len(raw))
        except zlib.error as exc:
            raise DedupeError("invalid_image", "corrupt PNG zlib stream") from exc
        raw.extend(out)
        if len(raw) > expected_raw_len:
            raise DedupeError("invalid_image", "inflated PNG data exceeds expected size")
        if decomp.eof:
            break
        remaining = decomp.unconsumed_tail or b""
    if len(raw) != expected_raw_len:
        raise DedupeError("invalid_image", "inflated PNG data length mismatch")

    bpp = _bytes_per_pixel(color_type)
    stride = width * bpp
    decoded = bytearray(width * height * bpp)
    for y in range(height):
        row_start = y * (stride + 1)
        filter_type = raw[row_start]
        row_data = raw[row_start + 1 : row_start + 1 + stride]
        if len(row_data) != stride:
            raise DedupeError("invalid_image", "truncated PNG scanline")
        prev_row = decoded[(y - 1) * stride : (y - 1) * stride + stride] if y > 0 else None
        current = bytearray(stride)
        for i in range(stride):
            left = current[i - bpp] if i >= bpp else 0
            up = prev_row[i] if prev_row else 0
            up_left = prev_row[i - bpp] if prev_row and i >= bpp else 0
            if filter_type == 0:
                val = row_data[i]
            elif filter_type == 1:
                val = (row_data[i] + left) & 0xFF
            elif filter_type == 2:
                val = (row_data[i] + up) & 0xFF
            elif filter_type == 3:
                val = (row_data[i] + (left + up) // 2) & 0xFF
            elif filter_type == 4:
                val = (row_data[i] + _paeth(left, up, up_left)) & 0xFF
            else:
                raise DedupeError("invalid_image", "invalid PNG filter type")
            current[i] = val
        decoded[y * stride : (y + 1) * stride] = current

    if color_type == 0:
        gray = bytes(decoded)
    elif color_type == 2:
        gray_buf = bytearray(width * height)
        for i in range(width * height):
            r = decoded[i * 3]
            g = decoded[i * 3 + 1]
            b = decoded[i * 3 + 2]
            gray_buf[i] = (299 * r + 587 * g + 114 * b + 500) // 1000
        gray = bytes(gray_buf)
    elif color_type == 4:
        alpha_buf = bytearray(width * height)
        for i in range(width * height):
            c = decoded[i * 2]
            a = decoded[i * 2 + 1]
            alpha_buf[i] = (c * a + 255 * (255 - a) + 127) // 255
        gray = bytes(alpha_buf)
    else:  # color_type == 6
        rgba_buf = bytearray(width * height)
        for i in range(width * height):
            r = decoded[i * 4]
            g = decoded[i * 4 + 1]
            b = decoded[i * 4 + 2]
            a = decoded[i * 4 + 3]
            luma = (299 * r + 587 * g + 114 * b + 500) // 1000
            rgba_buf[i] = (luma * a + 255 * (255 - a) + 127) // 255
        gray = bytes(rgba_buf)

    return GrayImage(width, height, gray)
