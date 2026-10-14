# REAL_WORLD_PROJECT — Advanced String Algorithms
> Log-threat scanner: Aho-Corasick multi-pattern service over rotated logs with KMP single-pattern fallback and a pattern-Staging pipeline.

## System and inputs
- Log shipper streams app logs in 64 MB rotated chunks; pattern set (200-2000 literals) versioned in config.
- Staging: new patterns run in count-only mode for 7 days before blocking mode; single urgent pattern can use KMP fast path within the hour.
- Match records carry (pattern version, chunk id, byte offset) for audit replay.

## Design
- Aho-Corasick automaton built per pattern version at deploy; build time and state count logged and alerted on 2x growth.
- Scanner streams chunks without loading whole files; overlapping-chunk boundary window re-scans the seam (documented width).
- KMP fast path for single-pattern emergencies bypasses automaton rebuild.

## Metrics
- Scan throughput MB/s per version and automaton build time/state count.
- Match rate per pattern (new-pattern staging dashboard) and false-positive-free verification (literals only).
- Seam re-scan byte overhead percentage.
- Missed-match canary: injected canary lines per chunk must all be reported.

## Failure modes
- Pattern-set explosion (20k regex-like literals submitted): version guard caps literal count and total length; excess goes to a second staged automaton, never silently dropped.
- Chunk-seam miss: seam window sized from the longest pattern; canary lines straddle seams to prove coverage.
- Automaton build spike blocks deploys: build runs async with the previous version serving until the new one verifies.
- Case/encoding mismatch: patterns normalized to the same case/encoding as the stream at build time, with the normalization logged.

## Rollout
1. Count-only mode on historical chunks; diff matches vs the existing grep pipeline until zero unexplained delta.
2. Blocking mode for the top-20 stable patterns; staging continues for the rest.
3. Full pattern set live with canary coverage on every chunk.

## Acceptance criteria
1. ushers reference ({he,she,his} -> she@1, he@2) verifies through the service scanner path.
2. Canary lines, including seam-straddling ones, are all reported in a chaos test.
3. Pattern-cap test: oversized set is staged, not dropped, with an alert.
4. Deploy with a broken pattern version keeps serving the previous automaton (test included).
5. Rollback pins the previous automaton version in one config change.

## Cost and contract notes
- Scanning priced per GB per pattern-version; automaton build cost amortized over chunks per version lifetime.
- Staging dashboards show per-pattern match rates for 7 days before any blocking promotion.
- Chunk storage retained 14 days so match offsets stay replayable for incident review.
- Contract: pattern versions immutable once published; emergency single-pattern path uses KMP with its own audit flag.
