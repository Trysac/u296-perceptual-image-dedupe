# Project record

## Objective

Find duplicate and near-duplicate images with average, difference and DCT perceptual hashes, bounded PNM and PNG decoding, Hamming distance and deterministic groups.

## Scope

- Public API: `GrayImage`, `load_image`, `image_hash`, `hamming`, `find_duplicates`, and `DedupeError`.
- Decoding: PNM P2/P3/P5/P6 with maxval 1-255 and header comments; PNG 8-bit non-interlaced color types 0, 2, 4, and 6 with all five filter types.
- Hashing: box-filter resize, `ahash`, `dhash`, `phash`, and Hamming distance.
- Grouping: single-link union-find over hashes with sorted groups and sorted members.
- CLI: folder scan with `--method`, `--max-distance`, and `--recursive`; exit codes 0, 1, and 2.

## Out of scope

- JPEG, WebP and GIF decoding; convert them first.
- Rotation or crop invariance.
- Deleting files.
- GPU execution.

## Timeline

The supplied specification and code contain no dated milestones.

## Effort metrics

Measured values only; a value that has not been measured stays "pending measurement".

| Metric | Value |
|---|---|
| Tokens (input / output) | 1895962 / 86875 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.1140 |

## Factory run u296 (measured from API usage)

| Date (UTC) | Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| 2026-11-11 | generation | deepseek-v4-pro | yes | 1878 | 22728 | 0 | 3328 | 0.0463 |
| 2026-11-11 | fix-1 | deepseek-flash | no | 28692 | 27278 | 0 | 940288 | 0.0235 |
| 2026-11-11 | audit | deepseek-flash | no | 22060 | 20979 | 0 | 458880 | 0.0173 |
| 2026-11-11 | fix-2 | deepseek-flash | no | 26948 | 6025 | 0 | 331264 | 0.0086 |
| 2026-11-11 | docs | deepseek-flash | no | 82368 | 9865 | 0 | 256 | 0.0183 |

Total: $0.1140. Prices: deepseek line, as measured by its adapter. Providers serve the current version of each model id, so the date tells which version answered; versions, launch stages and price sources per line are in the factory's model register (docs/MODELS.md).
