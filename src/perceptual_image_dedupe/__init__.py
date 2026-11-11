"""Perceptual image deduplication with stable perceptual hashes and bounded decoding."""

from __future__ import annotations

import logging

from .errors import DedupeError
from .group import find_duplicates
from .hash import hamming, image_hash
from .image import GrayImage
from .loader import load_image

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "DedupeError",
    "GrayImage",
    "find_duplicates",
    "hamming",
    "image_hash",
    "load_image",
]

__version__ = "0.1.0"
