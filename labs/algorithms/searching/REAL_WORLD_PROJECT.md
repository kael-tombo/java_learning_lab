# REAL_WORLD_PROJECT — Searching Track
> Production use-case with metrics + prevention. Track `searching`.

## Use-case: version lookup, feature-flag targeting, capacity planning
- System: backend service handling large inputs where searching is on the hot path.
- Why this algorithm: half-open binary search gives O(log n) exact bounds which meets latency SLO.
- Scope: input validation → solve → cache → observe → rollback.

## Architecture
```
Client → API (validate + auth) → Solver service (searching) → Cache (memo/short-TTL)
  → Metrics (latency/hit-rate/error) → Alerting → Rollback switch (feature flag)
```
- Stateless solver; scale horizontally; cache frequent subproblems.
- Async for n > threshold; sync fast-path for small n.

## Metrics (SLOs)
| Metric | Target | Alert |
|---|---|---|
| p95 solve latency | < 200 ms at n=10k | > 300 ms 5 min |
| Error rate | < 0.1% | > 0.5% |
| Cache hit rate | > 70% | < 50% |
| Memory per request | < 64 MB | > 128 MB |
| Correctness fuzz | 100% vs oracle nightly | any mismatch pages |

## Prevention (keep production safe)
- Validate: null/empty/size caps (reject n > max with 413 + async fallback).
- Overflow: long/BigInteger + addExact guards; property tests on extremes.
- DoS: timeouts + bulkheads; adversarial input rate-limited.
- Correctness: nightly fuzz vs brute force; golden-file regression suite.
- Rollout: feature flag + canary 1% → 25% → 100%; one-click rollback.
- Observability: structured logs (n, mode, ms); dashboard + trace IDs.

## Failure modes table
| Failure | Symptom | Mitigation |
|---|---|---|
| Adversarial worst-case input | p99 spike | size cap + async queue + optimized variant |
| Unsorted index served | wrong bounds | sort-assert + build checksum |
| OOM on huge n | restarts | streaming/rolling arrays + memory cap |
| Cache stampede | thundering herd | singleflight + jittered TTL |
| Predicate flip on deploy | wrong capacity | shadow-compare old/new predicate |

## Cost note
- Optimized variants (branchless/Eytzinger for static) cut compute ~2–10× vs naive; cache cuts repeat work.
- Document instance size before/after with benchmark numbers from MINI_PROJECT.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://algs4.cs.princeton.edu/11model/ (Princeton Algorithms — analysis model incl. binary search)
- https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Arrays.html (Java Arrays — binarySearch contract)

## Rollout plan (step-by-step)
1. Feature-flag solver; default OFF; shadow-mode logs only (1 day).
2. Canary 1 percent with latency and error dashboards; auto-rollback on SLO breach.
3. Ramp 25 percent to 100 percent over 3 days; freeze during peak traffic.
4. Post-deploy: weekly fuzz plus monthly capacity review.

## Request and response contract
- POST /solve with fields n, mode, payload returns 200 with answer, ms, traceId.
- 413 when input too large (queued jobId returned); 400 on validation failure.

## Incident playbook
- Pager fires on p95 over 300ms or errors over 0.5 percent: flip flag OFF, drain queue.
- Triage: check deploy diff, adversarial traffic spike, cache hit drop.
- Postmortem: add golden test plus update prevention table within 48h.

## Alternatives considered
- Naive brute force: simpler but misses SLO by 10-100x at scale.
- Third-party library: faster to ship, but opaque failure modes plus license cost.
- Precompute and cache-all: great hit rate until cardinality explodes; use TTL.

## Compliance and security notes
- Validate auth plus size caps; sanitize logs (no PII in payloads).
- Lookup keys may be user-linked; avoid logging raw keys.
- Data retention: keep benchmarks, drop raw user payloads after 30 days.

## Extended metrics appendix
| Signal | Collection | Dashboard |
|---|---|---|
| JVM heap and GC pause | JFR and Micrometer | Grafana panel |
| Queue depth async | counter | alert over 1000 |
| Fuzz nightly result | CI badge | notify on fail |
| Trace sampling | OpenTelemetry | tail-based sampling |
| Probes per query | histogram | alert on growth |

## Sizing worksheet
- Estimate QPS times p95 ms to get core count; add 30 percent headroom.
- Document instance size before and after with MINI_PROJECT numbers.
- Sorted index ≈ n entries resident; shard beyond RAM.
