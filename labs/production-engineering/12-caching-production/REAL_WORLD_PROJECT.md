# Lab 12: Caching Strategies & Cache Invalidation — Real World Project

## Scenario: "The Cache That Made It Worse"

You are a performance engineer on a retail platform: 11 Spring Boot 3 services, Java 21, Kubernetes, PostgreSQL primary + 2 read replicas, Redis 6 cluster (6 nodes, 32 GB), Caffeine in-process caches.

**The incident** — Sunday 09:40, one week before Black Friday. The Sunday-morning traffic is a quarter of peak, and the DB is at 12% CPU.

**What happened over 5 hours**:

1. **09:40** — `catalog-api` p99 rises from 180 ms to 3.4 s. Error rate 0.2% → 18%.
2. **09:52** — The DBA observes read-replica CPU climbing to 100% on both replicas. The primary is fine.
3. **10:15** — A responder adds a temporary Redis cache in front of the replica reads (a 10-minute change, deployed to 3 of 24 `catalog-api` pods). p99 recovers to 200 ms.
4. **10:31** — The other 21 pods are deployed. Within 90 seconds the Redis cluster goes to 100% CPU and the `catalog-api` p99 goes to 4.1 s — *worse* than before. The Redis hit ratio was never checked.
5. **11:20** — They revert the Redis cache. Latency returns to normal-ish, and the DB load returns. They conclude "Redis doesn't help".
6. **Over the following week** — Two more cache attempts are tried and reverted, each time with the same shape: added globally on low-confidence, measured by guess, reverted on the first bad graph.
7. **The actual cause** — found on day 8. A catalog `category` tree rebuild ran at 09:35 and replaced 240,000 product records. Every `products/{id}` cache entry from the previous generation was invalid by definition. The Caffeine caches (30-minute TTL, no jitter, per-pod, 24 pods) all expired within the same 30-minute window, so from 09:35 the DB absorbed 100% of reads. The replica CPU at 100% was the *symptom* of a synchronized mass expiry, not of traffic.
8. **Postmortem finding**: nobody knew the hit ratio, nobody knew which key classes were cached, the TTLs had no jitter, there was no `load duration` metric, and the cache's memory was not in anyone's budget. Every decision was made by intuition in an incident.

**Your job over 4 weeks**: build a caching strategy for the platform based on measurement. Per-class hit ratios, TTL policy from business staleness tolerances, stampede protection, memory budgets, and a rule that no cache ships without a proven justification.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Measure what you have (Day 1–4)

### 1.1 Cache inventory

For all caches in the estate (Caffeine and Redis): name, keys, TTL (and whether jittered), eviction policy, maximum size, estimated and measured bytes, which service owns it, which endpoints read it, which write paths invalidate it, and whether a write path *misses* invalidation.

**Deliverable 1 — Cache inventory** with a per-cache table and a "write-path coverage" column. Expect several caches invalidated by only some of their write paths.

### 1.2 Per-class hit ratio

Export `cache_requests_total{result}` with a bounded `keyClass` label for every cache. Compute `origin_load = Σ λ_class × (1 − h_class)` per cache.

**Deliverable 2 — Per-class attribution**: for each cache, the global hit ratio, the per-class hit ratio, and which class dominates origin load. Flag any cache where a class with a large `λ` has a near-zero hit ratio — those are the ones giving all the cost and none of the benefit.

### 1.3 Reconstruct Sunday

Rebuild the timeline: the category rebuild, the Caffeine expiry synchronisation, the replica CPU, the Redis rollout, and why Redis made it worse.

**Deliverable 3 — Causal analysis** with the expiry-synchronisation arithmetic (`240,000 keys ÷ 30-minute TTL` on 24 pods) and the Redis-overload analysis (why a 21-pod rollout against a saturated DB created a CPU storm in Redis).

### 1.4 Staleness tolerance survey

For each cached entity, ask the product owner: how stale may a customer see this, and what happens if they see something that stale? Record the answer with the owner's name.

**Deliverable 4 — Staleness tolerance register**: entity, owner, tolerance, current TTL, verdict (over-cached or under-cached), and the business consequence of the current TTL.

---

## Phase 2 — Decide what to cache (Day 4–8)

### 2.1 Break-even analysis per endpoint

For each read endpoint, compute:
```
h_min = 1 − (SLO_budget − L_cache) / L_origin
needed_origin_capacity = λ × (1 − h)
```
and classify the endpoint: latency win, capacity win, or not worth caching.

**Deliverable 5 — Per-endpoint caching verdict**, with the arithmetic. Include at least two endpoints where the verdict is "remove the cache" — removing a bad cache is a deliverable, not a failure.

### 2.2 Strategy per data class

Choose the pattern explicitly per class: cache-aside (default), write-through where writes are frequent and reads are critical, refresh-ahead for hot keys, no cache for zero-tolerance data (balances, entitlements, one-time tokens).

**Deliverable 6 — Strategy matrix** per entity: pattern, key, TTL (+jitter), invalidation trigger, staleness bound, owner.

### 2.3 Memory budget

Measure every cache's actual bytes (Caffeine `stats()`, Redis `MEMORY USAGE`, sampled `INFO memory`), and place them inside each service's container memory budget.

**Deliverable 7 — Cache memory budget per service**, with the container limit recomputed. Flag every service where the current cache memory does not fit — those are latent OOM-kills (Lab 07).

---

## Phase 3 — Implement the standard (Week 2)

### 3.1 TTL policy with jitter (platform standard)

```
ttl = base_tolerance × (1 + U(−0.10, +0.10))
```
plus a per-key random initial offset so first-population times do not align.

Apply to every cache; measure the post-deploy origin-load curve for each service.

**Deliverable 8 — Jitter rollout** with before/after origin-load curves for the two largest caches.

### 3.2 Stampede protection

For every hot key (top 10 by traffic): refresh-ahead (`refreshAfterWrite`) or soft TTL, plus `sync = true` where appropriate. For high read/low write classes, serve-stale-while-revalidate with a hard max-stale bound.

**Deliverable 9 — Stampede protection** for the top 10 hot keys, with the origin load measured during a forced expiry.

### 3.3 Invalidation correctness

For each cache, ensure exactly one write path per entity and that every mutation invalidates. Add version/epoch checks for multi-level caches (L1 + L2), with the version comparison as the guarantee and the broadcast as a hint.

Audit for: ORM bulk updates, admin endpoints, data-fix scripts, migration tools, and cross-service writers.

**Deliverable 10 — Invalidation audit** with the list of write paths that were missing invalidation, each fixed with a test.

### 3.4 Key correctness

Typed keys including tenant, locale, feature flags, API/schema version, and every filter parameter. A test suite for cross-tenant and cross-locale collisions, plus the HTTP `Cache-Control: private, no-store` check for personalised responses.

**Deliverable 11 — Key audit** with the collision test suite and the header test, and confirmation that no CDN/public cache can serve one user's response to another.

---

## Phase 4 — Guardrails (Week 2–3)

### 4.1 Metrics and alerts

Per cache: `hits`, `misses`, `load duration` (p50/p99), `evictions`, `entry count` vs maximum size, per-class hit ratio, `origin_requests_attributable_to_misses`, and for Redis `used_memory` vs `maxmemory` plus `evicted_keys`.

Alerts:
- `cache_load_duration_seconds` p99 > origin latency → origin is degrading; leading indicator.
- `hit_ratio` for any class < 50% over 1 h → warn (someone is caching the wrong things).
- `cache_evictions_total` rate > 0 sustained → cache is too small or a key class is evicting the useful entries.
- `used_memory/maxmemory > 0.85` → warn; `evicted_keys` increasing → the working set does not fit.
- `cache_origin_errors_total` > 0 → an origin failure has become a user-visible failure.
- Per-class `hit_ratio` drop > 20 points → the invalidation path may have changed.

**Deliverable 12 — Cache observability pack**: dashboards per cache class, alerts with thresholds tied to the Phase 1 measurements, and a runbook for each alert.

### 4.2 CI gates

- A cache added without a TTL, without jitter, or without a measured hit-ratio target fails the build.
- A new `@Cacheable` without an `@CacheEvict` on the owning write path fails.
- A cache key that omits a tenant/locale parameter (detected by a code convention check) fails.
- Cache memory in the manifest exceeding the budget in the service's cache plan fails.
- A new cache whose break-even hit ratio is not documented fails.

**Deliverable 13 — CI gates** blocking all five deliberately bad cache PRs, each with a specific message.

---

## Phase 5 — Prove it (Week 3)

Replay Sunday and Black Friday shapes in staging:

| Scenario | Injection | Success criteria |
|---|---|---|
| S1 | Baseline Sunday traffic (25% of peak) | p99 < 250 ms, hit ratio at target, no alerts |
| S2 | The Sunday event: a category rebuild invalidating 240,000 products | origin load bounded; no synchronized expiry; p99 stays within SLO |
| S3 | 24-pod staggered cache rollout with Redis at the new load | no Redis CPU storm; p99 stable throughout |
| S4 | Hot key expiry (top key, forced) | origin load from that key < 5 rps; p99 unaffected |
| S5 | Penetration flood: 800 rps of non-existent ids | origin load reduced ≥ 30× |
| S6 | Replica failover during peak | cache serves the read path; p99 within SLO; staleness bounded |
| S7 | Origin (WireMock) returning 503 with a full cache | behaviour per the max-stale policy; metric and alert fire |
| S8 | Dropped invalidation broadcast (L1/L2) | reload, never a wrong answer; proven by test |
| S9 | `pageSize=10,000` request to a cached list endpoint | rejected by the server-side cap; cache not flooded |
| S10 | Deployment with cache pre-warm | no origin spike during warm-up |
| S11 | Black Friday peak (4× the Sunday shape) | p99 < 400 ms, replica CPU < 60%, no origin saturation |
| S12 | A cache deliberately misconfigured (no jitter, single global TTL) | the CI gate blocks it before merge |

**Deliverable 14 — Cache resilience report** with all twelve scenarios, measured origin load, hit ratio, and p99, and fixes for anything missed.

---

## Phase 6 — Operate it (Week 3–4)

- **Runbooks**: `RUNBOOK_CACHE_MISS_SURGE.md`, `RUNBOOK_REDIS_SATURATION.md`, `RUNBOOK_CACHE_STAMPEDE.md`, `RUNBOOK_STALE_DATA_REPORT.md`, `RUNBOOK_CACHE_MEMORY.md`.
- **Ownership**: every cache has a named owner team, in the catalogue, in the alerts, and in the escalation path.
- **Game day**: S2, S4, S6 with the on-call in business hours; measure the time to the correct hypothesis (which should be seconds now, given `load duration`).
- **Capacity review**: before Black Friday, review every cache's hit ratio, TTL, jitter, and memory, and remove the caches that fail the break-even test.
- **Standards**: TTL-from-tolerance, jitter, stampede protection, key completeness, and memory budgeting documented in the platform caching standard and embedded in the service template.

**Deliverable 15 — Operational package**: runbooks, ownership catalogue, game-day report, caching standard, template changes.

---

## Phase 7 — Quantify and institutionalize (Week 4)

| Metric | Before | After |
|---|---|---|
| Caches with a measured, per-class hit ratio | 0 / 19 | 19 / 19 |
| Caches with jittered TTLs | 2 / 19 | 19 / 19 |
| Hot keys with stampede protection | 0 | top 10 protected, refresh-ahead |
| Caches with a documented staleness tolerance | 0 | 19 |
| Caches removed after break-even analysis | — | 3 |
| Write paths missing invalidation | 7 | 0 |
| Caches inside a container memory budget | 6 / 19 | 19 / 19 |
| P99 during a mass invalidation | 3.4 s | < 350 ms |
| Origin load after a synchronized expiry | 100% of reads | bounded by jitter + refresh-ahead |
| Redis CPU during a fleet-wide cache rollout | 100% | < 45% |
| Mean time to diagnose a cache-related latency spike | ~4 h (three failed attempts) | < 10 min |
| Cache decisions made without data | all | none |

Institutionalize: caching standard in the template; every cache requires a documented tolerance, break-even analysis, jitter, and budget before merge; the per-class hit-ratio dashboard is part of the service's standard dashboard; a quarterly cache review removes the ones that stopped earning their memory.

**Deliverable 16 — Business case + institutionalization**, including the cost of the Redis memory and the CPU cost of caching, traded against the availability improvement.

---

## Deliverables checklist

- [ ] Phase 1 cache inventory, per-class attribution, causal analysis, staleness register.
- [ ] Phase 2 per-endpoint verdict, strategy matrix, memory budget.
- [ ] Phase 3 jitter rollout, stampede protection, invalidation audit, key audit.
- [ ] Phase 4 observability pack and five CI gates.
- [ ] Phase 5 twelve-scenario cache resilience report.
- [ ] Phase 6 runbooks, ownership, game day, caching standard.
- [ ] Phase 7 before/after business case + institutionalization.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "The cache expired" | Mass-expiry synchronisation arithmetic across 24 pods, and why Redis amplified it |
| Measurement | "Hit ratio is 78%" | Per-class hit ratio and origin-load attribution; global number shown to hide the dominant class |
| Decision | "Cache the hot endpoints" | Break-even hit ratios per endpoint, including caches that should be removed |
| TTL | "We set 30 minutes" | Tolerance → TTL → jitter, with a business owner per tolerance |
| Stampede | "We added jitter" | Breakdown/avalanche/penetration distinguished, each mitigated and measured |
| Multi-level | "We broadcast invalidation" | Version-check guarantee; a dropped broadcast proven to cause a reload, not wrong data |
| Memory | "Redis has 32 GB" | Per-service cache bytes inside the container budget; latent OOM-kills identified |
| Proof | "Load test with cache on" | Replays the category rebuild, the 24-pod rollout, replica failover, origin 503, penetration flood |
| Operations | "Watch the hit ratio" | `load duration` leading indicator, eviction alerts, ownership, game day |
| Sustainability | "We documented it" | Template, CI gates, quarterly review, and caches actually removed |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Redis documentation — `allkeys-lru` / eviction, `OBJECT FREQ`, and `EXPIRE`/`SETEX` semantics** — https://redis.io/docs/latest/develop/reference/eviction/ (and https://redis.io/docs/latest/commands/object-freq/) — the authoritative reference for memory-policy behaviour under a working set larger than `maxmemory`, for `allkeys-lru` versus `volatile-*` semantics, and for the `OBJECT FREQ` counter used in the LFU policy and in hit/miss estimation discussions. Verify the current default `maxmemory-policy` and whether `volatile-ttl`/`volatile-lfu` variants exist in your Redis version rather than assuming.
2. **Caffeine — `Cache` design and eviction/refresh documentation** — https://github.com/ben-manes/caffeine/wiki — the authoritative source for `expireAfterWrite` versus `refreshAfterWrite` (the serve-stale-while-revalidate pairing), `expireAfterAccess`, `maximumSize`/`maximumWeight`, `recordStats()`/`CacheStats`, `CacheLoader.reload` behaviour, and the guidance on concurrency (`AsyncCacheLoader`) for refresh. Use it to justify the "jitter your TTL" and "refresh ahead of expiry" recommendations rather than asserting them; the library's `expireAfter` accessors expose `variable` timing, which is the cleanest place to implement jitter.

Additional anchors worth verifying: Spring Boot's cache abstraction property names for your version (`spring.cache.redis.*`, `spring.cache.caffeine.spec` string form) — these are strings and easy to typo silently; the `CaffeineCacheManager` behaviour when a `@Cacheable` method returns `null` (whether `allowNullValues` is enabled by default in your version, which determines whether negative caching works out of the box); and HTTP `Cache-Control` directive semantics for `private`/`no-store`/`stale-while-revalidate` against RFC 9111 rather than blog posts.

---

## Reflection questions

1. Twenty-four pods with a 30-minute TTL created a synchronized expiry. Is jitter the right fix, or is the real problem that the TTL is longer than the rebuild cycle?
2. The Redis cache was deployed globally on low confidence and reverted in an hour. What process would have made a 10-minute, 3-pod canary the default?
3. Nobody knew the hit ratio. Why is hit ratio a better health metric than cache latency, and why is `load duration` the better leading indicator?
4. The team concluded "Redis doesn't help". What evidence would have separated "Redis is a bad idea here" from "Redis was deployed wrongly"?
5. Which caches in your estate would you remove, and what would you need to measure to justify removing them?
