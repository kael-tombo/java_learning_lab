# Distributed Caching (Deep) - Real World Project

## Project: Coherent Caching Across a Microservice Fleet

### Objective
Design a caching layer for a fleet of independently deployed services that cannot use
centralised invalidation messages, and guarantee a bounded staleness that product has signed
off on.

### Why This Is a Real Problem
The moment services are deployed independently, a publish in service A cannot synchronously
invalidate caches in service B. The realistic options are a shared cache with event-driven
invalidation, versioned keys, or bounded TTL — and the choice must be made per data class,
not once for the whole system.

### Architecture Overview
```
 svc-A ─┐                     ┌─ svc-B ─┐
 svc-C ─┼─▶ Redis cluster ────┼─ svc-D ─┤   (shared cache, versioned keys)
        │                     └─ svc-E ─┘
        └─▶ outbox ─▶ bus ─▶ invalidation consumer ─▶ Redis version bump

 Per-class policy:
   catalogue    versioned keys + event invalidation, TTL 10 min
   user profile versioned keys, event invalidation, TTL 60s
   permissions  NO cache (authorisation must be current)
   pricing      local L1, 30s TTL, single-flight to Redis
```

### Phase 1: Classify the Data (Week 1)
1. Inventory every cached object with its owner service and consumers
2. For each, answer: how stale may a consumer tolerate, and what happens if it is staler?
3. Sort into: `cacheable with event invalidation`, `cacheable with TTL only`,
   `never cache`
4. Expect a meaningful `never cache` bucket. Permissions and balance checks belong there.

### Phase 2: Choose the Invalidation Mechanism per Class (Week 2)
| Class | Mechanism | Rationale |
|---|---|---|
| catalogue | versioned keys + bus invalidation | large, read-mostly, high volume |
| user profile | versioned keys + bus invalidation | frequently read, must be fresh-ish |
| pricing | TTL only + local L1 | high churn, staleness is self-correcting |
| permissions | none | staleness is a security finding |

1. Implement versioned keys: `obj:{tenant}:{id}@{version}`, version in a separate metadata key
2. Publish invalidation from the owning service's outbox so a publish never loses the event
3. Consumer bumps the version; old entries become unreachable and expire naturally
4. TTL as the backstop for lost invalidations — set from the class's staleness tolerance

### Phase 3: Absorb the Hot Keys (Week 3)
1. In-process L1 with a very short TTL (5–30s) in front of Redis
2. Single-flight per L1 to collapse L1 misses
3. Distributed single-flight (Redis lock, 30s) for L1 misses so a whole fleet does not storm
4. Detect hot keys: track per-key request rate; a single key above a threshold gets a
   dedicated cache node or a precomputed value
5. Bound value size and set `maxmemory-policy` deliberately; document which policy you chose
   and why (LRU-allkeys evicts session data too)

### Phase 4: Survive the Cache Being Down (Week 4)
1. Every read path has a defined behaviour when Redis is unavailable — choose per class:
   catalogue serves stale; pricing serves stale; profile fails closed
2. Implement and test circuit-breaking with jittered backoff, not a fixed retry loop
3. Measure origin capacity: during a full cache outage, can the origin take the load? If not,
   the cache is load-bearing and you need a documented degradation path
4. Run a full-outage drill and record actual origin behaviour

### Phase 5: Prove the Guarantees (Week 5+)
1. Max-staleness metric per class, with an SLO and alert
2. Integration test: publish a change, assert every service sees it within the class's TTL
3. Dashboard: hit ratio per class, L1 hit ratio, single-flight collapses, origin QPS,
   invalidation lag p99, cache-outage events
4. Runbook: "cache unavailable" — which classes degrade, which fail, what the fallback is

### Deliverables
1. Data classification with staleness tolerances and product sign-off
2. Versioned-key cache client plus the outbox-driven invalidation consumer
3. Hot-key detection, single-flight, and L1 sizing based on measured working set
4. Max-staleness SLO with alert, outage drill report, and the degradation runbook

### Success Criteria
- Observed staleness per class stays within its declared TTL, verified by integration test
- A full cache outage degrades every class according to the documented policy
- Origin survives the outage without exceeding its capacity limit
- Zero cross-tenant cache leakage, proven by a test that varies every key dimension

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Redis Documentation —
  https://redis.io/docs/
  Use for: eviction policy semantics, `maxmemory` behaviour, and the difference between a
  cache instance and a system of record. Verify policy names and defaults against your
  deployed version — `allkeys-lru` and `volatile-lru` behave very differently when keys
  carry no TTL.
- Apache Kafka Documentation, design section —
  https://kafka.apache.org/documentation/#design
  Use for: the durable log used to carry invalidation events without loss. The ordering and
  retention guarantees here are what let a consumer re-derive a missed invalidation.

### Estimated Time
6-7 weeks part-time