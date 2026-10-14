# REAL_WORLD_PROJECT — Sorting and Searching Deep Track
> Genomic k-mer index builder: suffix-array-backed substring queries over a 50 MB reference with external-merge construction and a successor-query API.

## System and inputs
- Reference string (up to 50 MB) ingested per release; query API serves count/presence plus up to 100 occurrence offsets per pattern.
- Builder runs offline with a memory cap; queries serve online from the memory-mapped index.
- Release gate: 10k seeded patterns checked against naive search before promotion.

## Design
- Doubling suffix-array construction with external-merge passes when the working set exceeds the cap; LCP array built alongside for count queries.
- Query path: binary search over SA for the pattern interval, LCP walk for the count, capped offset list for locate.
- Bounded-universe side index (vEB-style over encoded 12-mers) accelerates short-pattern prefiltering; labeled with its universe limit.

## Metrics
- Build wall time and peak memory vs the cap; query p50/p99 by pattern length bucket.
- Release-gate mismatch count (must be zero) and canary-pattern latency.
- Offset-cap truncation rate (queries hitting the 100-offset cap).
- Prefilter hit rate and time saved vs direct SA search.

## Failure modes
- Reference exceeding the builder cap: external passes engage automatically with progress logging; cap breach without engagement pages.
- Highly repetitive reference (poly-A stretches) blowing up occurrence lists: offset cap plus count-first responses keep latency bounded.
- Stale index after reference update: versioned indexes with atomic swap; queries carry the index version in responses.
- Prefilter universe overflow (k-mer longer than encoding): falls back to direct SA search with a logged event.

## Rollout
1. Build the index for the current reference; gate against naive search on 10k patterns.
2. Shadow-serve production queries; compare answers and latency buckets.
3. Promote with versioned swap; retain the previous index one release.

## Acceptance criteria
1. Release gate passes 10k/10k pattern checks including banana-class edge cases.
2. Oversized-reference test engages external passes without breaching the cap.
3. Repetitive-pattern test respects the offset cap with count-first answers.
4. Version-swap test shows zero mixed-version responses.
5. Rollback restores the previous index version within the documented time.

## Cost and contract notes
- Index build costed per release (wall time x worker price); query fleet sized from the p99-by-length table.
- Offset-cap truncation reported per query class so consumers know what locate does not return.
- Prefilter universe limit documented in the API (12-mer encoding); longer patterns take the direct path automatically.
- Contract: query responses carry index version, method path (prefilter/SA), and truncation flag.
