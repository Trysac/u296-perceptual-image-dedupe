"""Deterministic duplicate grouping via union-find on Hamming distances."""

from __future__ import annotations

from collections.abc import Mapping

from .errors import DedupeError
from .hash import hamming


class _BKNode:
    __slots__ = ("children", "hash_value", "keys")

    def __init__(self, hash_value: int, key: str):
        self.hash_value = hash_value
        self.keys = [key]
        self.children: dict[int, _BKNode] = {}


class _BKTree:
    def __init__(self) -> None:
        self.root: _BKNode | None = None

    def insert(self, hash_value: int, key: str) -> None:
        if self.root is None:
            self.root = _BKNode(hash_value, key)
            return
        node = self.root
        while True:
            d = hamming(hash_value, node.hash_value)
            if d == 0:
                # Same hash: add key to existing node
                node.keys.append(key)
                return
            if d in node.children:
                node = node.children[d]
            else:
                node.children[d] = _BKNode(hash_value, key)
                return

    def query(self, target_hash: int, max_distance: int) -> list[_BKNode]:
        if self.root is None:
            return []
        result: list[_BKNode] = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            d = hamming(target_hash, node.hash_value)
            if d <= max_distance:
                result.append(node)
            for edge_dist, child in node.children.items():
                if abs(d - edge_dist) <= max_distance:
                    stack.append(child)
        return result


def find_duplicates(
    hashes: Mapping[str, int],
    *,
    max_distance: int = 10,
    max_items: int = 100_000,
) -> list[list[str]]:
    """Group keys whose hashes are within ``max_distance`` Hamming distance.

    Groups contain at least two members, are sorted internally by key, and are
    returned ordered by their first key.
    """
    if max_distance < 0:
        raise DedupeError("invalid_argument", "max_distance must be non-negative")
    if len(hashes) > max_items:
        raise DedupeError("too_many_images", f"more than {max_items} hashes")

    keys = list(hashes)
    parent = {k: k for k in keys}

    def find(k: str) -> str:
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    tree = _BKTree()
    for k in keys:
        tree.insert(hashes[k], k)

    nodes: list[_BKNode] = []
    stack = [tree.root] if tree.root else []
    while stack:
        node = stack.pop()
        nodes.append(node)
        stack.extend(node.children.values())

    # Keys stored in one node share the same hash, hence distance 0: collapse them
    # once instead of unioning every pair of keys at query time (that would be
    # quadratic in the number of duplicate hashes).
    for node in nodes:
        for k in node.keys[1:]:
            union(node.keys[0], k)

    for node in nodes:
        for other in tree.query(node.hash_value, max_distance):
            union(node.keys[0], other.keys[0])

    groups_by_root: dict[str, list[str]] = {}
    for k in keys:
        root = find(k)
        groups_by_root.setdefault(root, []).append(k)

    groups: list[list[str]] = []
    for members in groups_by_root.values():
        if len(members) >= 2:
            members_sorted = sorted(members)
            groups.append(members_sorted)
    groups.sort(key=lambda g: g[0])
    return groups
