"""Perceptual hashing functions: ahash, dhash, phash and Hamming distance."""

from __future__ import annotations

import math
from typing import Literal

from .errors import DedupeError
from .image import GrayImage


def _resize_box(img: GrayImage, target_width: int, target_height: int) -> list[list[float]]:
    """Resize using the specified box filter, returning float pixels."""
    W = img.width
    H = img.height
    result = [[0.0] * target_width for _ in range(target_height)]
    for y in range(target_height):
        ys = (y * H) // target_height
        ye = ((y + 1) * H) // target_height
        if ye <= ys:
            ye = ys + 1
        for x in range(target_width):
            xs = (x * W) // target_width
            xe = ((x + 1) * W) // target_width
            if xe <= xs:
                xe = xs + 1
            total = 0.0
            count = 0
            for sy in range(ys, min(ye, H)):
                for sx in range(xs, min(xe, W)):
                    total += img.pixels[sy * W + sx]
                    count += 1
            result[y][x] = total / count
    return result


def _bits_to_int(bits: list[int]) -> int:
    result = 0
    for bit in bits:
        result = (result << 1) | bit
    return result


def _ahash(img: GrayImage) -> int:
    resized = _resize_box(img, 8, 8)
    vals = [resized[y][x] for y in range(8) for x in range(8)]
    mean = sum(vals) / 64.0
    bits = [1 if v > mean else 0 for v in vals]
    return _bits_to_int(bits)


def _dhash(img: GrayImage) -> int:
    resized = _resize_box(img, 9, 8)
    bits: list[int] = []
    for y in range(8):
        for x in range(8):
            bits.append(1 if resized[y][x + 1] > resized[y][x] else 0)
    return _bits_to_int(bits)


def _phash(img: GrayImage) -> int:
    resized = _resize_box(img, 32, 32)
    N = 32
    values = [resized[y][x] for y in range(N) for x in range(N)]
    # Subtracting the mean leaves every non-DC coefficient unchanged in exact arithmetic,
    # while keeping the sums small enough that a constant shift of the pixels cannot flip bits.
    mean = sum(values) / (N * N)
    centered = [[resized[y][x] - mean for x in range(N)] for y in range(N)]
    coeff = [[0.0] * 8 for _ in range(8)]
    for u in range(8):
        for v in range(8):
            total = 0.0
            if u == 0 and v == 0:
                # The DC term is the plain sum, as defined by the DCT-II.
                for x in range(N):
                    for y in range(N):
                        total += resized[y][x]
            else:
                for x in range(N):
                    cu = math.cos(math.pi / N * (x + 0.5) * u)
                    for y in range(N):
                        cv = math.cos(math.pi / N * (y + 0.5) * v)
                        total += centered[y][x] * cu * cv
            coeff[u][v] = total
    median_vals = [coeff[u][v] for u in range(8) for v in range(8) if not (u == 0 and v == 0)]
    median_vals.sort()
    med = median_vals[len(median_vals) // 2]
    bits = [1 if coeff[u][v] > med else 0 for u in range(8) for v in range(8)]
    return _bits_to_int(bits)


def image_hash(
    img: GrayImage,
    method: Literal["ahash", "dhash", "phash"] = "dhash",
) -> int:
    """Compute a 64-bit perceptual hash for ``img`` using the requested method."""
    if method not in ("ahash", "dhash", "phash"):
        raise DedupeError("invalid_argument", "unknown hash method")
    if method == "ahash":
        return _ahash(img)
    if method == "dhash":
        return _dhash(img)
    return _phash(img)


def hamming(a: int, b: int) -> int:
    """Return the Hamming distance (number of differing bits) between two integers."""
    return (a ^ b).bit_count()
