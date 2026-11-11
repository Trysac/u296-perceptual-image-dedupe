# perceptual-image-dedupe

[![PyPI version](https://img.shields.io/pypi/v/trysac-perceptual-image-dedupe)](https://pypi.org/project/trysac-perceptual-image-dedupe/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-perceptual-image-dedupe)](LICENSE)
[![CI](https://github.com/Trysac/u296-perceptual-image-dedupe/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u296-perceptual-image-dedupe/actions/workflows/ci.yml)

Find duplicate and near-duplicate images with average, difference and DCT perceptual hashes, bounded PNM and PNG decoding, Hamming distance and deterministic groups

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-perceptual-image-dedupe
# or
uv add trysac-perceptual-image-dedupe
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import perceptual_image_dedupe

# normalize() trims surrounding whitespace and lower-cases the text.
print(perceptual_image_dedupe.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    perceptual_image_dedupe.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
