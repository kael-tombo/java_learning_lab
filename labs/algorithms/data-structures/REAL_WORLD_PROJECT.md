# REAL_WORLD_PROJECT — Data Structures Track
> Feature-flag evaluation engine: trie-matched flag keys, Fenwick-metered rollout exposure, union-find cohort dedup, and a heap-scheduled experiment queue.

## System and inputs
- Flag definitions (key patterns with wildcards) versioned in config; evaluation requests carry (user id, attributes, timestamp).
- Exposure metering counts evaluations per flag per hour for billing and guardrails.
- Experiment queue schedules A/B ramp steps by priority with rescheduling on guardrail trips.

## Design
- Trie matches flag-key patterns with prefix counts for the admin UI (how many flags share a prefix).
- Fenwick tree over hourly buckets answers sliding exposure sums in O(log n) for guardrail checks.
- Union-find dedups overlapping cohort definitions so users in two cohorts count once in shared analyses.
- Binary heap schedules ramp steps; guardrail trip re-inserts the step with backoff.

## Metrics
- Evaluation p99 latency with per-structure breakdown (trie match, exposure sum, cohort find).
- Exposure-guard trip rate and heap reschedule counts.
- Cohort-dedup merge rate (how often overlap is actually found).
- Config-version adoption lag across serving nodes.

## Failure modes
- Wildcard explosion (pattern matching everything): compile-time pattern audit rejects over-broad wildcards with the match count.
- Exposure-counter overflow at high QPS: 64-bit counters with a documented rotation policy, never silent wrap.
- Cohort merge storm (everyone overlaps): union-find stays near-constant, but the analysis falls back to sampled counting with a logged event.
- Stale flag config on some nodes: version header on evaluations; lagging nodes flagged in the adoption dashboard.

## Rollout
1. Shadow-evaluate production traffic; compare decisions vs the legacy if/else engine exactly.
2. Serve internal flags live; guardrails armed on exposure sums.
3. Full migration with the experiment queue driving ramps.

## Acceptance criteria
1. Shadow week shows zero decision mismatches on sampled evaluations.
2. Over-broad wildcard test is rejected at compile time with the match count.
3. Exposure guard trips and reschedules a ramp step in the chaos test.
4. Cohort overlap test counts shared users once (verified on a hand-built case).
5. Rollback pins the legacy engine back within the documented time.

## Cost and contract notes
- Evaluation latency budget split per structure so regressions attribute correctly (trie vs Fenwick vs find).
- Exposure-guard trips costed in delayed experiment value; backoff parameters versioned with flags.
- Config-adoption lag SLO per node cohort; laggards paged after the documented window.
- Contract: evaluation responses carry flag-config version for reproducibility of billing disputes.
