# VISION — Count-Min Sketch (27)

Vision: answer "how many times did I see X?" in streams with bounded memory and one-sided error.

## Mental models
- A d×w counter grid; each item hashes to one cell per row; add(x) increments all of them.
- Estimate = min across rows; collisions only inflate, never deflate (overestimate-only).
- Width w controls error ε (≈ 2/w with N-count bound), depth d controls failure probability δ.
- Think of it as a lossy histogram: you trade exactness for O(wd) memory.

## Decision table
| Need | Use |
|---|---|
| Exact counts, bounded keys | HashMap / long[] |
| Frequency over sliding window | Deque of sketches |
| Top-k heavy hitters + counts | Count-Min + heap |
| Distinct count | HyperLogLog (lab 26) |
| Turnstile (negatives) streams | Count sketch (median, not min) |
| Point query with updates at scale | Count-Min Sketch |

## Career path
- Shows up in: RedisBloom (Count-Min), Datadog/analytics pipelines, DB query optimizers.
- Interview angle: streaming algorithms, probabilistic structures, one-sided error reasoning.
- Next labs: 28 (MinHash/SimHash), 26 (HyperLogLog) — build a probabilistic-toolbox narrative.

## Done when
- [ ] Can derive w ≈ e/ε and d ≈ ln(1/δ) from the sketch definition
- [ ] One-sided error proven on a small counterexample
- [ ] Mini + real-world project shipped with benchmark
