# Architecture

## Purpose

`trysac-perceptual-image-dedupe` is a small, dependency-free Python library: Find duplicate and near-duplicate images with average, difference and DCT perceptual hashes, bounded PNM and PNG decoding, Hamming distance and deterministic groups

## Shape

```text
caller code --> perceptual_image_dedupe (public API in __init__.py)
                    |
                    +-- pure functions, no I/O, no global state
```

- **Public API**: the names listed in `__all__` of `src/perceptual_image_dedupe/__init__.py`. Anything else is
  internal and may change without a major version.
- **Errors**: invalid input raises built-in exceptions (`ValueError`, `TypeError`) with a clear
  message; the library never prints or exits.
- **Side effects**: none. If a feature needs I/O, isolate it in its own module behind a small
  interface and record the choice in an ADR.

## Quality contract

`scripts/check.py` is the single definition of the gates; `fabrica.json` tells the factory and CI
how to run it. See [TESTING.md](TESTING.md).

## Decisions

Architecture decisions are recorded in [decisions/](decisions/) as numbered ADRs.
