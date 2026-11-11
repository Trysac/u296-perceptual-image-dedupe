# Deterministic perceptual hashing without external imaging libraries

Status: accepted (generated, pending human review)

## Context

The utility must find near-duplicate images with stable hashes across versions, using only the Python standard library.

## Decision

Decode PNM and a constrained subset of PNG manually, implement exact box-filter resize and DCT-II with integers/floats, and use a BK-tree for efficient pair discovery.

## Consequences

Supported formats are limited; JPEG/WebP/GIF require pre-conversion. Hash values are stable across library versions on the same platform and Python build.
