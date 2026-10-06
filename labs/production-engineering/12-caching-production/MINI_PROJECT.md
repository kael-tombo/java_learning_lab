# Lab 12: Caching Strategies & Cache Invalidation — Mini Project

## Project: `CacheLab` — Measure, Then Decide, Then Defeat Every Stampede

**Time**: 10–14 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, Caffeine, Redis (Testcontainers or docker-compose), PostgreSQL, Micrometer/Prometheus, k6 or Gatling, WireMock for origin simulation

Build a caching layer for a catalogue + basket service, and spend most of your time proving where it helps, where it does not, and how it fails.

---

## Part 1 — The service

```
[k6 loadgen] → [catalog-api:8080] ──JDBC──→ [postgres:5432]
                     │
                     ├── L1 Caffeine
                     └── L2 Redis:6379
```

Four endpoints with deliberately different characteristics:

| Endpoint | Origin cost | Staleness tolerance | Write rate |
|---|---|---|---|
| `GET /api/v1/categories` | 5 ms | hours | ~never |
| `GET /api/v1/products/{id}` | 30 ms | ~60 s | 50/s |
| `GET /api/v1/search?q=` | 120 ms | ~10 s | 50/s |
| `GET /api/v1/basket/{id}` | 8 ms | **zero** | user-driven |

The point of the shape: one endpoint where caching is obviously right, one where it barely matters, one where the origin is expensive, and one where caching is *wrong*.

```yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 60s
      cache-null-values: true
  redis:
    timeout: 200ms
    lettuce:
      pool:
        max-active: 32
        max-idle: 16
```

---

## Part 2 — Measure before optimising (Part 2 is not optional)

### 2.1 Baseline with no cache

```bash
k6 run baseline.js       # 500 rps for 3 minutes against all four endpoints
```

Record per endpoint: p50/p95/p99, DB queries/s, DB CPU, origin CPU, and the *load duration* metric you will add.

**Deliverable**: `BASELINE.md` — the no-cache reference table. Every later number is compared against this.

### 2.2 Naive cache, then a real verdict

Add a single global cache with one TTL and measure.

```java
@Cacheable(value = "api", key = "#id")
public ProductDto product(UUID id) { return mapper.toDto(repo.findById(id).orElseThrow()); }
```

Then compute the break-even hit ratio per endpoint:

```
h_min = 1 − (SLO_budget − L_cache) / L_origin
```

| Endpoint | `L_origin` | SLO budget | `h_min` | Measured `h` | Verdict |
|---|---|---|---|---|---|
| categories | 5 ms | 250 ms | negative (any `h`) | ~0.99 | latency no, capacity yes |
| products | 30 ms | 250 ms | negative | ~0.93 | yes |
| search | 120 ms | 250 ms | negative | ~0.35 | yes (capacity + latency) |
| basket | 8 ms | 250 ms | negative | **n/a — must not cache** | **no** |

**Deliverable**: `CACHE_VERDICT.md` — per endpoint, whether caching helps latency, helps capacity, or is wrong, with the arithmetic and the measured hit ratio. This document is the honest version of "we added Redis".

### 2.3 Per-class hit ratio attribution

Export metrics with a bounded `keyClass` label (never the key itself):

```java
MeterRegistry registry;

@Around("execution(* com.example.catalog..*Service.*(..))")
Object observe(ProceedingJoinPoint pjp) {
    var t = Timer.builder("cache.access")
        .tag("keyClass", cacheKeyClassifier.classify(pjp.getArgs()))
        .tag("result", "miss")
        .register(registry);
    return t.record(() -> pjp.proceed());
}
```

Grafana: hit ratio **per class**, plus `origin_load = Σ λ_class × (1 − h_class)`.

Show the deliberately hidden class: `basket` has a 78% global hit ratio but contributes the majority of origin load. A global hit-ratio dashboard improves while the DB stays saturated.

**Deliverable**: per-class attribution table showing which class to fix first, with the numbers.

---

## Part 3 — TTL policy as code

```java
@Configuration
class CachePolicy {

    /**
     * TTL is derived from the business staleness tolerance, with jitter so a mass
     * expiry cannot become an origin storm. Jitter is the single most important line here.
     */
    record Entry(String name, Duration tolerance, boolean jittered) {}

    static final Map<String, Entry> POLICY = Map.of(
        "categories",  new Entry("categories", Duration.ofHours(6), true),
        "products",    new Entry("products",   Duration.ofSeconds(60), true),
        "search",      new Entry("search",     Duration.ofSeconds(10), true),
        // "basket" is deliberately absent: zero staleness tolerance => never cache.
        "absent",      new Entry("absent",     Duration.ofSeconds(30), true));   // negative cache
}
```

```java
Caffeine.newBuilder()
    .expireAfterWrite(jitter(POLICY.get("products").tolerance(), 0.10))   // 60s ± 6s
    .refreshAfterWrite(jitter(Duration.ofSeconds(40), 0.10))              // serve-stale while revalidate
    .maximumSize(50_000)
    .recordStats()
    .build();
```

```java
static Duration jitter(Duration base, double fraction) {
    double factor = 1 + ThreadLocalRandom.current().nextDouble(-fraction, fraction);
    return Duration.ofMillis(Math.round(base.toMillis() * factor));
}
```

**Deliverable**: `TTL_POLICY.md` — the table of tolerance → TTL → jitter, with the business owner who signed off each tolerance, and the expected staleness (`TTL/2`) versus worst case (`TTL`) for each.

---

## Part 4 — Defeat every stampede variant

### 4.1 Breakdown (hot key)

```java
// one product id receives 40,000 rps in the load test
k6 run hotkey.js
```

Watch `origin_load` spike to 40,000 rps; DB connections exhausted; everything times out.

Then fix, one at a time, measuring origin load each time:

| Fix | Implementation | Origin load | Note |
|---|---|---|---|
| none | plain `sync=false` | 40,000 rps | 5× over origin capacity |
| TTL jitter only | `expireAfterWrite(60s ± 6s)` | ~40,000/s but in a burst | worse than nothing if 40k expire together |
| `sync = true` | single-flight loader | 1 request per expiry | waiters occupy threads; check pool saturation |
| refresh-ahead | `.refreshAfterWrite(40s)` | ≈ 1/40 rps | p99 unaffected; preferred |
| soft TTL | Caffeine `refreshAfterWrite` + scheduler | ≈ 1/refresh rps | best |

**Deliverable**: `STAMPEDE.md` with the measured table and the concurrency analysis for the `sync=true` variant (39,999 waiters × 50 ms → Little's Law on your thread pool).

### 4.2 Avalanche (mass expiry)

Repopulate the whole cache at deploy time (pre-warm), then let all entries expire together with a fixed TTL.

Then enable jitter and re-run. Measure the origin load curve over time — a delta versus a plateau.

**Deliverable**: two origin-load-vs-time tables (delta vs plateau) with the peak values.

### 4.3 Penetration (absent keys)

```bash
k6 run penetration.js   # 800 rps of random non-existent UUIDs
```

Add negative caching, then a bloom filter, and measure:

```
origin_load_absent = λ_invalid × P(absent)
negative cache TTL 30 s  →  origin load ≈ λ/30
bloom filter (p=0.001)  →  origin load ≈ 0 (no false negatives, rare false positives only)
```

```java
// Guard against negative caching hiding a create
@CacheEvict(cacheNames = "absent", key = "#id")
public Product create(...) { ... }        // invalidate the negative entry on create
```

**Deliverable**: `PENETRATION.md` with origin load for: no negative cache / negative cache / bloom filter, plus the create-invalidation test.

---

## Part 5 — Two-level cache with version-based invalidation

### 5.1 L1 (Caffeine) + L2 (Redis)

```java
record Versioned<T>(T value, long version) {}
```

### 5.2 Version store and check

```java
@Service
@RequiredArgsConstructor
class VersionedCache {
    private final StringRedisTemplate redis;
    private final Cache<Long, Long> localVersions;      // per-key version cache

    long currentVersion(String key) {
        String v = redis.opsForValue().get("ver:" + key);
        return v == null ? 0L : Long.parseLong(v);
    }

    /** Bump on every write. Publish a hint; the version check is the guarantee. */
    public void invalidate(String key) {
        Long next = redis.opsForValue().increment("ver:" + key);
        redis.convertAndSend("cache:invalidate", key + ":" + next);      // hint only
    }

    @SuppressWarnings("unchecked")
    public <T> Optional<T> get(String key, Class<T> type) {
        var local = (Versioned<T>) localCache.getIfPresent(key);
        long v = currentVersion(key);
        if (local != null && local.version() >= v) {
            return Optional.ofNullable(local.value());      // version matches => safe to serve
        }
        String raw = redis.opsForValue().get(key);
        if (raw == null) return Optional.empty();
        T parsed = mapper.readValue(raw, type);
        localCache.put(key, new Versioned<>(parsed, v));
        return Optional.of(parsed);
    }
}
```

### 5.3 Prove the broadcast can be lost safely

```bash
# Block pub/sub to simulate a dropped broadcast
docker compose stop redis-pubsub     # or firewall the channel
```

Then:
1. Update a product (version bumps, L2 evicted, L1 *not* notified).
2. Read it repeatedly from the pod holding the stale L1 entry.
3. Observe: the version check detects the mismatch and reloads. **Never a stale value.**

**Deliverable**: `MULTILEVEL.md` — the design, the L1 TTL (short, e.g. 30 s), the version check, and the test proving a dropped broadcast causes a reload, not a wrong answer.

---

## Part 6 — Serve stale while revalidate, with a bound

```java
Caffeine.newBuilder()
    .expireAfterWrite(Duration.ofSeconds(90))          // hard bound: the value is unusable after this
    .refreshAfterWrite(Duration.ofSeconds(45))         // served stale, refreshed in background
    .build();
```

Demonstrate the failure mode too: set the origin (WireMock) to return 503, wait past `expireAfterWrite`, and observe what your service does.

- Correct: it fails loudly (503 to the caller, `origin_errors_total` increments, alert fires).
- Incorrect: it keeps serving the 90-second-old value forever.

Add an explicit max-stale policy and a metric:

```java
if (age > maxStale) { metrics.counter("cache.stale_over_bound").increment(); throw new OriginUnavailable(); }
```

**Deliverable**: `STALE_POLICY.md` with the bound, the behaviour when the origin is down, and the metric/alert that makes it visible.

---

## Part 7 — Cache memory in the container budget

```java
long estimatedBytes = cache.policy().eviction().get().map(e -> ((long) e.getMaximum()) * 3_000).orElse(0L);
```

Measure actual usage with `Cache.stats()` and `redis MEMORY USAGE <key>`.

Now do the thing the Lab 07 OOM-kill taught you: run the service in a container sized *without* the cache in the budget, with the cache at maximum size, and watch the cgroup kill it.

```bash
docker run -m 900m orders-api    # heap 600m, but 390 MB of L1 cache + metaspace + stacks + direct > 900m
```

Fix: reduce `maximumSize` to fit, or raise the container limit, and document the arithmetic.

**Deliverable**: `MEMORY_BUDGET.md` — measured cache bytes, the revised container memory budget with every term, and the reproduction of the OOM-kill.

---

## Part 8 — Cache-key correctness audit

```java
record ProductKey(UUID productId, UUID tenantId, String locale, String currency, int schemaVersion) {}
```

Test cases that must all pass:
1. Same id, different tenant → different entries (no cross-tenant leak).
2. Same id, same tenant, different locale → different entries.
3. Same id, same tenant, same locale, different `schemaVersion` → different entries.
4. Two different filter combinations that would concatenate identically without a delimiter (`a=1,b=23` vs `a=12,b=3`) → different entries.
5. `null` vs `""` → do not collide.

Then an HTTP-layer check: verify that any personalised response carries `Cache-Control: private, no-store` (or that your CDN is configured with `Vary` on the right headers), and add a test that fails if a per-user response is ever marked publicly cacheable.

**Deliverable**: `KEY_AUDIT.md` with the five tests and the header test.

---

## Acceptance Criteria

- [ ] `BASELINE.md` provides the no-cache reference for every later comparison.
- [ ] `CACHE_VERDICT.md` proves, per endpoint, whether caching helps latency, capacity, or is wrong — including the endpoint that must not be cached, with a test proving it is not.
- [ ] Per-class hit-ratio attribution identifies the class dominating origin load despite a healthy global number.
- [ ] `TTL_POLICY.md` maps business staleness tolerance → TTL + jitter, with an owner per tolerance.
- [ ] `STAMPEDE.md` measures breakdown, avalanche, and penetration with the origin-load number for each mitigation.
- [ ] `MULTILEVEL.md` proves a dropped broadcast causes a reload, not a wrong answer.
- [ ] `STALE_POLICY.md` defines and tests the hard max-stale bound, including the origin-down failure mode.
- [ ] `MEMORY_BUDGET.md` shows the cache inside a container memory budget and reproduces the OOM-kill when it is not.
- [ ] `KEY_AUDIT.md` passes all five collision tests plus the HTTP cache-header test.

---

## Stretch

- Replace L2 JSON serialisation with a compact binary format and measure the p99 delta on the hit path.
- Implement a cache-warming endpoint and measure how pre-warming changes the post-deploy origin curve.
- Add an adaptive per-key TTL that shortens for keys with high write rates (`hitchhiking`/frequency-aware expiry) and measure the hit-ratio gain.
- Build a "cache decision service" that computes break-even hit ratios from each endpoint's origin latency and SLO, and have CI fail when a new cache has an unproven justification.
