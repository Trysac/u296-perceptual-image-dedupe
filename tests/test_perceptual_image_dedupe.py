"""Behavior tests for the public API of perceptual_image_dedupe."""

from __future__ import annotations

import perceptual_image_dedupe


def test_public_api_exports() -> None:
    expected = {
        "DedupeError",
        "GrayImage",
        "find_duplicates",
        "hamming",
        "image_hash",
        "load_image",
    }
    assert expected.issubset(set(perceptual_image_dedupe.__all__))
    for name in expected:
        assert hasattr(perceptual_image_dedupe, name)


def test_hamming_through_public_api() -> None:
    assert perceptual_image_dedupe.hamming(0b1011, 0b0001) == 2


def test_version_is_semver() -> None:
    parts = perceptual_image_dedupe.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
