# REAL_WORLD_PROJECT — Searching Track
> Account-lookup service: 200M-key read path with a hash fast path, sorted-snapshot fallback, and a miss-cost dashboard.

## System and inputs
- Nightly snapshot builds a sorted key array plus an open-addressing hash index; lookups serve from memory-mapped files.
- Query mix: 95 percent hits, 5 percent misses (enumeration probes); adversarial bursts of misses possible during scans.
- Correctness anchor: every build verified against a sampled exact map before promotion.

## Design
- Hash fast path with the load factor capped by build config; misses fall through to exponential search on the sorted array for range-neighbor answers.
- Interpolation used only for the uniform timestamp secondary index, with a skew monitor that disables it automatically.
- Negative-result cache (short TTL) absorbs miss bursts without re-probing the full structure.

## Metrics
- Hit/miss p50/p99 latency split (never blended), miss-burst rate, negative-cache hit rate.
- Load factor and probe-count distribution per build.
- Interpolation skew monitor value with auto-disable events logged.
- Build verification pass/fail gating promotion.

## Failure modes
- Miss-burst scan (enumeration): negative cache plus rate limiting; alert on 10x miss-rate deviation.
- Skewed timestamp index silently degrades interpolation: monitor disables it and logs the switch to binary.
- Snapshot corruption: build verification fails, previous snapshot keeps serving, page on two consecutive failures.
- Hash DoS via crafted keys: keyed hash seed rotated per build; rotation event logged.

## Rollout
1. Shadow-read production queries against the new index; compare answers and latencies.
2. Serve 10 percent of reads; watch the hit/miss split dashboards.
3. Full cutover with the previous snapshot retained one week for instant rollback.

## Acceptance criteria
1. Shadow week shows zero answer mismatches on sampled queries.
2. Miss-burst chaos test stays within latency budget via the negative cache.
3. Skew test disables interpolation automatically with a logged event.
4. Corrupt-build test keeps the old snapshot serving.
5. Rollback restores the previous snapshot within the documented time.

## Cost and contract notes
- Snapshot build cost (sort + hash) amortized over nightly queries; build-time budget alert at 2x median.
- Negative-cache memory capped separately; eviction logged so miss-burst accounting stays exact.
- Timestamp-index skew monitor thresholds versioned with the index build, reviewed monthly.
- Contract: lookup responses carry snapshot version and method (hash/exponential/interpolation) for latency attribution.
