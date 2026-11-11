"""Error type for perceptual_image_dedupe."""

from __future__ import annotations

from typing import Literal


class DedupeError(Exception):
    """Raised for all library-specific failures.

    Attributes:
        code: Machine-readable error code.
        message: Human-readable detail, truncated to 200 characters.
    """

    def __init__(
        self,
        code: Literal[
            "input_too_large",
            "image_too_large",
            "invalid_image",
            "unsupported_image",
            "too_many_images",
            "invalid_argument",
        ],
        message: str = "",
    ) -> None:
        self.code = code
        self.message = message[:200]
        super().__init__(f"{code}: {self.message}" if self.message else code)
