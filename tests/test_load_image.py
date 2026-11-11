"""Tests for load_image and format decoding."""

from __future__ import annotations

import struct
import zlib

from perceptual_image_dedupe import DedupeError, GrayImage, load_image

from .conftest import make_png


def test_pnm_p5_basic() -> None:
    data = b"P5\n2 1\n255\n\x00\xff"
    img = load_image(data)
    assert img == GrayImage(2, 1, b"\x00\xff")


def test_pnm_p5_scaling() -> None:
    data = b"P5\n2 1\n1\n\x00\x01"
    img = load_image(data)
    assert img == GrayImage(2, 1, b"\x00\xff")


def test_pnm_p6_red_to_gray() -> None:
    data = b"P6\n1 1\n255\n\xff\x00\x00"
    img = load_image(data)
    assert img == GrayImage(1, 1, bytes([76]))  # (299*255+500)//1000 = 76


def test_pnm_p3_comments_and_scaling() -> None:
    data = b"P3\n# comment\n2 1\n255\n255 0 0 0 255 0"
    img = load_image(data)
    expected = bytes(
        [
            (299 * 255 + 587 * 0 + 114 * 0 + 500) // 1000,
            (299 * 0 + 587 * 255 + 114 * 0 + 500) // 1000,
        ]
    )
    assert img == GrayImage(2, 1, expected)


def test_pnm_invalid_maxval() -> None:
    data = b"P5\n1 1\n256\n\x00"
    try:
        load_image(data)
    except DedupeError as e:
        assert e.code == "invalid_image"
    else:
        raise AssertionError("expected DedupeError")


def test_png_gray_1x1() -> None:
    png = make_png(1, 1, 0, b"\x80")
    img = load_image(png)
    assert img == GrayImage(1, 1, b"\x80")


def test_png_rgb_green_to_gray() -> None:
    png = make_png(1, 1, 2, b"\x00\xff\x00")
    img = load_image(png)
    # (299*0 + 587*255 + 114*0 + 500)//1000 = 150
    assert img == GrayImage(1, 1, bytes([150]))


def test_png_rgba_transparent_to_white() -> None:
    png = make_png(1, 1, 6, b"\x00\x00\x00\x00")
    img = load_image(png)
    assert img == GrayImage(1, 1, bytes([255]))


def test_png_gray_alpha_composite() -> None:
    png = make_png(1, 1, 4, b"\x80\x80")
    img = load_image(png)
    # (128*128 + 255*127 + 127)//255 = (16384+32385+127)//255 = 48896//255 = 191
    assert img == GrayImage(1, 1, bytes([191]))


def test_png_bad_crc() -> None:
    png = bytearray(make_png(1, 1, 0, b"\x00"))
    # Corrupt the stored CRC of the final IEND chunk: the decoder must report invalid_image.
    png[-1] ^= 0xFF
    try:
        load_image(bytes(png))
    except DedupeError as e:
        assert e.code == "invalid_image"
    else:
        raise AssertionError("expected DedupeError")


def test_png_interlaced_unsupported() -> None:
    # Build IHDR with interlace=1 manually, plus IDAT/IEND
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 1)
    idat_data = zlib.compress(b"\x00\x00")

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    png = sig + chunk(b"IHDR", ihdr_data) + chunk(b"IDAT", idat_data) + chunk(b"IEND", b"")
    try:
        load_image(png)
    except DedupeError as e:
        assert e.code == "unsupported_image"
    else:
        raise AssertionError("expected DedupeError")


def test_png_16bit_unsupported() -> None:
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 16, 0, 0, 0, 0)
    png = (
        sig
        + chunk(b"IHDR", ihdr_data)
        + chunk(b"IDAT", zlib.compress(b"\x00\x00\x00"))
        + chunk(b"IEND", b"")
    )
    try:
        load_image(png)
    except DedupeError as e:
        assert e.code == "unsupported_image"
    else:
        raise AssertionError("expected DedupeError")


def test_pnm_p2_non_numeric_sample() -> None:
    try:
        load_image(b"P2\n1 1\n255\nabc")
    except DedupeError as e:
        assert e.code == "invalid_image"
    else:
        raise AssertionError("expected DedupeError")


def test_pnm_p2_negative_sample() -> None:
    try:
        load_image(b"P2\n1 1\n255\n-1")
    except DedupeError as e:
        assert e.code == "invalid_image"
    else:
        raise AssertionError("expected DedupeError")


def test_pnm_p5_sample_above_maxval() -> None:
    try:
        load_image(b"P5\n1 1\n100\n\xc8")
    except DedupeError as e:
        assert e.code == "invalid_image"
    else:
        raise AssertionError("expected DedupeError")


def test_pnm_p3_sample_above_maxval() -> None:
    try:
        load_image(b"P3\n1 1\n255\n256 0 0")
    except DedupeError as e:
        assert e.code == "invalid_image"
    else:
        raise AssertionError("expected DedupeError")


def test_pnm_header_integer_too_long() -> None:
    data = b"P5\n" + b"9" * 5000 + b" 1\n255\n\x00"
    try:
        load_image(data)
    except DedupeError as e:
        assert e.code == "invalid_image"
    else:
        raise AssertionError("expected DedupeError")


def test_pnm_sample_integer_too_long() -> None:
    data = b"P2\n1 1\n255\n" + b"9" * 20
    try:
        load_image(data)
    except DedupeError as e:
        assert e.code == "invalid_image"
    else:
        raise AssertionError("expected DedupeError")


def test_load_image_input_too_large() -> None:
    data = b"x" * (104_857_601)
    try:
        load_image(data)
    except DedupeError as e:
        assert e.code == "input_too_large"
    else:
        raise AssertionError("expected DedupeError")


def test_png_dimensions_too_large() -> None:
    # Build a PNG header claiming 10000x10000, but without actual raster data.
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", 10000, 10000, 8, 0, 0, 0, 0)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    png = sig + chunk(b"IHDR", ihdr_data) + chunk(b"IEND", b"")
    try:
        load_image(png)
    except DedupeError as e:
        assert e.code == "image_too_large"
    else:
        raise AssertionError("expected DedupeError")


def test_png_all_filter_types() -> None:
    # 4x1 image with each filter type, gray values
    for ft in range(5):
        png = make_png(4, 1, 0, bytes([0, 1, 2, 3]), filter_type=ft)
        img = load_image(png)
        assert img == GrayImage(4, 1, bytes([0, 1, 2, 3]))


def test_png_upscale_from_1x1() -> None:
    png = make_png(1, 1, 0, b"\x80")
    img = load_image(png)
    assert img.width == 1 and img.height == 1
