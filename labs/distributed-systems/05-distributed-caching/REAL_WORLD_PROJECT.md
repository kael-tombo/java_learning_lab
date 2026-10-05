# Distributed Caching - Real World Project

## Project: Catalogue Cache Redesign for a Traffic-Spiking Retail Site

### Objective
Take a catalogue layer that is missing on peak days and stabilises origin load, without ever
serving one customer's data to another.

### Why This Is a Real Problem
Caching bugs are asymmetric: it works perfectly for months and then fails during the traffic
spike you built it for. The realistic hazards here are stampede on promotion day, cache
poisoning from one bad upstream response, and — the one that ends careers — a cache key
missing a dimension that makes responses tenant-specific.

### Architecture Overview
```
  Client ─▶ CDN (static + edge TTL)
              │ miss
              ▼
          App tier ─▶ Redis cluster (hot catalogue, short TTL)
              │ miss          │ single-flight via Redis lock
              ▼               ▼
          Origin (RDS + read replica)  ◀── async invalidation on publish
```

### Phase 1: Measure Before Touching (Week 1)
1. Find the actual slow queries: enable slow-query logging, rank by total time *consumed*
2. For each candidate, record current hit ratio (probably zero), origin p99, and DB CPU
3. Set the goal as an SLO: catalogue p99 < 100ms at 3x current peak
4. Write down the staleness tolerance with the merchandising team — that number sets every
   TTL in this project

### Phase 2: Key Design and Isolation (Week 2)
1. Key shape: `cat:v3:{region}:{tenant}:{category}:{sku}` — every dimension that changes the
   response body must be in the key
2. Serialise responses per category, not per SKU, so a 10k-SKU listing is one entry
3. Namespace per environment; never share a Redis instance across prod and staging
4. Cap value size (e.g. 256KB). A single oversized entry can evict the entire working set
5. Add a `X-Cache: HIT|MISS|STALE` header so you can measure reality from the edge

### Phase 3: Stampede Protection (Week 3)
1. Single-flight in-process with a per-key `CompletableFuture` map
2. Cross-process coalescing via a short-lived Redis lock (30s TTL, not a blocking mutex)
3. Serve **stale while revalidating** on origin failure — a slightly old catalogue beats a
   503 on promotion day
4. Negative caching with a short TTL (5s) so bad SKU lookups cannot storm origin
5. Add `Retry-After` to origin calls so failures degrade instead of amplifying

### Phase 4: Invalidation That Cannot Race (Week 4)
1. Publishing a catalogue change writes an invalidation event, not a direct delete
2. Consumer deletes with a short debounce (e.g. 500ms) to collapse edit storms
3. Short TTLs as the safety net: even if an invalidation is lost, staleness is bounded
4. Test: publish 1000 changes in a second, confirm the working set converges within 30s

### Phase 5: Operate (Week 5+)
1. Dashboards: hit ratio by key prefix, origin QPS, single-flight coalescing count, evictions
2. Alerts: hit ratio drop >10 points, eviction rate spike, origin error rate
3. A "cache purge" runbook that is boring because nothing depends on manual purging
4. Rehearse promotion day: 3x traffic for 2 hours, watch the SLO hold

### Deliverables
1. Redis cluster design with key schema and TTL policy per key type
2. Cache client with single-flight, stale-while-revalidate, and negative caching
3. Invalidation consumer with debounce plus convergence test
4. Before/after dashboard and a promotion-day rehearsal report

### Success Criteria
- Catalogue p99 < 100ms at 3x baseline traffic
- Origin QPS during peak stays flat versus off-peak
- No cross-tenant or cross-region response leakage, verified by test
- Any staleness after a publish is under 30 seconds, measured

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Redis Documentation —
  https://redis.io/docs/
  Use for: eviction policies, memory limits, and the distinction between a cache instance
  and a system of record. Verify policy names against the version you run — `allkeys-lru`
  and `volatile-lru` behave very differently when keys have no TTL.
- AWS Architecture Blog / Well-Architected guidance via the Amazon CloudWatch metrics
  overview —
  https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-metrics-monitoring.html
  Use for: modelling cache hit rate and origin-throttling metrics as CloudWatch metrics so
  the SLO above is actually observable. Verify the exact namespace names before wiring
  alarms.

### Estimated Time
5-6 weeks part-time