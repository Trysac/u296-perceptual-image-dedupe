"""Tests for perceptual hash functions."""

from __future__ import annotations

from perceptual_image_dedupe import DedupeError, GrayImage, hamming, image_hash


def _gray_from_2d(rows: list[list[int]]) -> GrayImage:
    h = len(rows)
    w = len(rows[0])
    data = bytes(pixel for row in rows for pixel in row)
    return GrayImage(w, h, data)


def test_dhash_gradient_full() -> None:
    # 9x8 image, each row linearly increasing by 10 per column
    rows = [[x * 10 for x in range(9)] for _ in range(8)]
    img = _gray_from_2d(rows)
    assert image_hash(img, "dhash") == 0xFFFFFFFFFFFFFFFF


def test_dhash_rows_reversed_zero() -> None:
    # Same as above but each row reversed: right neighbour always less, so all bits 0
    rows = [[(8 - x) * 10 for x in range(9)] for _ in range(8)]
    img = _gray_from_2d(rows)
    assert image_hash(img, "dhash") == 0


def test_ahash_left_right_split() -> None:
    # 8x8 image, left half 0, right half 255, mean=127.5 => left below mean, right above
    rows = [[0 if x < 4 else 255 for x in range(8)] for _ in range(8)]
    img = _gray_from_2d(rows)
    # Bits: for each row, four 0s then four 1s => 0b00001111 repeated 8 times = 0x0f0f0f0f0f0f0f0f
    assert image_hash(img, "ahash") == 0x0F0F0F0F0F0F0F0F


def test_phash_similar_small_change() -> None:
    # Image with all pixels <=200 and its version +10 should differ by at most 1 bit
    rows = [[x % 201 for x in range(32)] for _ in range(32)]
    img1 = _gray_from_2d(rows)
    rows2 = [[min(x + 10, 200) for x in row] for row in rows]
    img2 = _gray_from_2d(rows2)
    h1 = image_hash(img1, "phash")
    h2 = image_hash(img2, "phash")
    assert hamming(h1, h2) <= 1


def test_unknown_method_error() -> None:
    img = GrayImage(1, 1, b"\x00")
    try:
        image_hash(img, "invalid")  # type: ignore[arg-type]
    except DedupeError as e:
        assert e.code == "invalid_argument"
    else:
        raise AssertionError("expected DedupeError")


def test_hamming_distance() -> None:
    assert hamming(0b1011, 0b0001) == 2


def test_upscaling_1x1_ahash_all_zeros() -> None:
    img = GrayImage(1, 1, b"\x00")
    # Resized to 8x8 all zeros, mean=0, all bits 0
    assert image_hash(img, "ahash") == 0


def test_uniform_image_ahash_all_zeros() -> None:
    rows = [[128] * 8 for _ in range(8)]
    img = _gray_from_2d(rows)
    assert image_hash(img, "ahash") == 0
