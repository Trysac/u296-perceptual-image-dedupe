"""Tests for the command-line interface."""

from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path

from perceptual_image_dedupe.__main__ import main

from .conftest import make_png


def _write_pnm(path: Path, width: int, height: int, data: bytes) -> None:
    header = f"P5\n{width} {height}\n255\n".encode()
    path.write_bytes(header + data)


def _run(argv: list[str]) -> tuple[int, str, str]:
    """Run ``main`` capturing stdout and stderr."""
    stdout = StringIO()
    stderr = StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = stdout, stderr
    try:
        rc = main(argv)
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
    return rc, stdout.getvalue(), stderr.getvalue()


def test_cli_duplicates_found(tmp_path: Path) -> None:
    # Row-major gradient: dhash has every bit set for both files, so they group.
    gradient = bytes(x * 10 for _ in range(8) for x in range(9))
    (tmp_path / "a.png").write_bytes(make_png(9, 8, 0, gradient))
    _write_pnm(tmp_path / "b.pgm", 9, 8, gradient)
    (tmp_path / "x.bmp").write_bytes(b"not an image")

    rc, stdout, stderr = _run([str(tmp_path)])

    assert rc == 1
    assert stdout.strip().splitlines() == ["a.png b.pgm"]
    assert "skipped: x.bmp unsupported_image" in stderr


def test_cli_no_duplicates(tmp_path: Path) -> None:
    increasing = bytes(x * 10 for _ in range(8) for x in range(9))
    decreasing = bytes((8 - x) * 10 for _ in range(8) for x in range(9))
    (tmp_path / "a.png").write_bytes(make_png(9, 8, 0, increasing))
    (tmp_path / "b.png").write_bytes(make_png(9, 8, 0, decreasing))

    rc, stdout, stderr = _run([str(tmp_path)])

    assert rc == 0
    assert stdout.strip() == ""
    assert stderr.strip() == ""


def test_cli_missing_folder(tmp_path: Path) -> None:
    rc, _, stderr = _run([str(tmp_path / "nonexistent")])

    assert rc == 2
    assert "folder not found" in stderr


def test_cli_unreadable_file_reports_invalid_image(tmp_path: Path) -> None:
    # Header is complete but the one-byte raster is missing.
    (tmp_path / "bad.pgm").write_bytes(b"P5\n1 1\n255\n")

    rc, stdout, stderr = _run([str(tmp_path)])

    assert rc == 0
    assert stdout.strip() == ""
    assert "skipped: bad.pgm invalid_image" in stderr
