"""Tests for find_duplicates."""

from __future__ import annotations

from perceptual_image_dedupe import DedupeError, find_duplicates


def test_single_link_group() -> None:
    hashes = {"a": 0x0, "b": 0x3, "c": 0xFF}
    assert find_duplicates(hashes, max_distance=2) == [["a", "b"]]
    hashes2 = {"a": 0x0, "b": 0x3, "c": 0xF}
    assert find_duplicates(hashes2, max_distance=2) == [["a", "b", "c"]]


def test_group_sorting() -> None:
    hashes = {"b": 0x0, "a": 0x1, "c": 0x0}
    groups = find_duplicates(hashes, max_distance=1)
    assert groups == [["a", "b", "c"]]


def test_groups_sorted_by_first_key() -> None:
    hashes = {"c": 0xF0, "b": 0xF1, "a": 0x10, "d": 0x11}
    groups = find_duplicates(hashes, max_distance=1)
    assert groups == [["a", "d"], ["b", "c"]]
    # Keys are grouped by single link, so a chain of near hashes merges into one group.
    assert find_duplicates({"a": 0x0, "b": 0x1, "c": 0x10}, max_distance=1) == [["a", "b", "c"]]


def test_too_many_items_error() -> None:
    hashes = {f"k{i}": i for i in range(100_001)}
    try:
        find_duplicates(hashes)
    except DedupeError as e:
        assert e.code == "too_many_images"
    else:
        raise AssertionError("expected DedupeError")


def test_negative_max_distance_error() -> None:
    try:
        find_duplicates({"a": 0}, max_distance=-1)
    except DedupeError as e:
        assert e.code == "invalid_argument"
    else:
        raise AssertionError("expected DedupeError")


def test_no_duplicates() -> None:
    hashes = {"a": 0x0, "b": 0xFFFF}
    assert find_duplicates(hashes) == []
