# VISION — MinHash & SimHash (28)

Vision: compress set similarity and near-duplicate detection into a handful of integers.

## Mental models
- MinHash: the minimum hash per set, per permutation; estimate Jaccard directly from agreement rate.
- More permutations ≈ more bands ≈ finer estimate; k permutations → k signature values.
- SimHash: weighted vote per bit position; cosine-ish similarity → Hamming distance.
- Both turn O(|A∩B|) work into O(k) integer comparisons; MinHash = sets, SimHash = text.
- LSH banding converts similarity into buckets for candidate pairs (avoid O(n²)).

## Decision table
| Need | Use |
|---|---|
| Jaccard over sets | MinHash signatures |
| Near-duplicates in text | SimHash / Hamming |
| Candidate-pair discovery | LSH banding |
| Exact dedup | SHA-256 content hash |
| Plagiarism / shingle overlap | MinHash |
| Web-page near-dup clustering | SimHash (Google-style) |

## Career path
- Shows up in: dedup pipelines, recommender candidate generation, plagiarism detectors.
- Interview angle: LSH, Jaccard/cosine, trade of signature size vs accuracy.
- Combines with lab 26 (cardinality) and 27 (frequency) for streaming analytics.

## Done when
- [ ] Derive P(agree) = J for MinHash with one example
- [ ] SimHash sign/flip demonstrated on a tiny bit vector
- [ ] Mini + real-world project shipped with candidate-pair timings
