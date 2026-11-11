"""Image data model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GrayImage:
    """A grayscale image stored as row-major bytes, one byte per pixel."""

    width: int
    height: int
    pixels: bytes

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if len(self.pixels) != self.width * self.height:
            raise ValueError("pixels length must equal width * height")
