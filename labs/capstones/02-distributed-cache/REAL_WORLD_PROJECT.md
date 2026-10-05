# Distributed Cache — REAL WORLD PROJECT

## Context

A fintech serves a mobile app through 34 backend services. Six months ago the
platform team deployed a Redis cluster to absorb load; the hit rate is now 61%
and falling, the origin database p99 is 840ms at peak, and the incident last
month was a 4-minute origin outage that turned into a 40-minute partial
outage because every request for one hot account table missed simultaneously.
You own the caching layer for the platform.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Traffic | 180k rps peak, 2,100 rps mean (86x peak/mean ratio) |
| Read:write | 97:3 |
| Cache | Redis Cluster, 48 nodes, 6 replicas, 1.4TB RAM, 3.2TB used |
| Data | 90M accounts, 2.4M accounts hot (2.7%), 41,000 keys in one table |
| Origin | Postgres primary, 12 read replicas, p99 840ms under cache-miss storms |
| SLO | p99 < 80ms, availability 99.99% |
| Compliance | PCI scope includes the cache: encrypt in transit, audit access |
| Constraint | cannot invalidate a key pattern across 48 nodes on a hot path |

## Architecture (target)

```
 app -> [service cache layer (local, 256MB, LRU, request-scoped coalescing)]
        |  miss
        v
      [Redis Cluster: 48 nodes]
        |  - 3 tiers: request/response cache, entity cache, computed cache
        |  - bloom filters in front (per service, local)
        |  - hot-key sharding for the 41,000-key table
        |  - pull-based versioned invalidation, not broadcast
        |  miss
        v
      [read replicas] (max staleness budget: 5s for account balances)
```

## Key Implementation — the hit rate decline, diagnosed

The hit rate fell 94% → 61% over six months while traffic grew 2x. The causes,
in order of contribution:

| Cause | Contribution | Fix |
|---|---|---|
| No TTL discipline: 31% of keys never expire, so the working set exceeds RAM and evicts hot keys | 19pp | TTL tiers + an explicit eviction policy per key class |
| Cache-of-cache missing: every miss goes to Redis, most of which are not in Redis either | 14pp | local per-pod cache with coalescing |
| Cardinality explosion from a new request-shape header being included in the key | 9pp | key schema with a documented, versioned component list |
| Eviction policy `allkeys-lru` on keys with bimodal access (hot + long-tail) | 8pp | `allkeys-lfu` or segmented LFU for the entity tier |
| No bloom filter, so negative lookups always reach Redis | 6pp | per-service bloom filters |

The bloom filter deserves a note: 22% of lookups are for keys that do not
exist, and each was a Redis round trip that returned null. A 1% false-positive
bloom filter over 90M keys costs about 1.2MB per service and eliminates 99% of
those round trips entirely.

## Key Implementation — the four fixes, with numbers

**Fix 1: TTL tiers, enforced by key class.**

```java
public enum Tier {
    REQUEST( Duration.ofSeconds(30),  "idempotent GET; safe to be very short"),
    ENTITY(  Duration.ofMinutes(5),  "reference data; change events invalidate"),
    ACCOUNT( Duration.ofSeconds(5),  "balances: 5s staleness matches the replica lag"),
    COMPUTED(Duration.ofMinutes(15), "aggregates; recomputed anyway, so longer is fine"),
    NEGATIVE(Duration.ofSeconds(10), "known-missing keys, so a typo does not hammer the origin");

    final Duration ttl;
    final String rationale;
    Tier(Duration ttl, String rationale) { this.ttl = ttl; this.rationale = rationale; }
}
```

The 5-second account TTL is not arbitrary. It matches the read-replica lag
budget, so a cached account is never *staler* than a replica read would be.
That alignment is the kind of decision that prevents a whole class of
"which number is right" incident.

**Fix 2: a local per-pod cache with request coalescing.** This is the one that
recovers the hit rate, because it removes Redis round trips rather than making
them cheaper.

```java
public final class LocalCache<K, V> {
    private final Map<K, Entry<V>> map;
    private final int capacity;
    private final ConcurrentHashMap<K, CompletableFuture<V>> inflight = new ConcurrentHashMap<>();

    /**
     * Two effects, both necessary:
     *   - a local TTL (seconds) so the local copy cannot outlive the global one
     *   - single-flight, so a hot key expiring on 200 pods does not produce
     *     200 simultaneous Redis misses and 200 origin loads
     * The second effect is the one that prevented the 4-minute outage becoming
     * a 40-minute one.
     */
    public V get(K key, Function<K, V> loader) {
        Entry<V> e = map.get(key);
        if (e != null && !e.expired(now())) { e.touch(now()); return e.value(); }

        CompletableFuture<V> mine = new CompletableFuture<>();
        CompletableFuture<V> existing = inflight.putIfAbsent(key, mine);
        if (existing != null) {
            return unwrap(existing.join());       // join the in-flight load
        }
        try {
            V v = loader.apply(key);
            admit(key, v);
            mine.complete(v);
            return v;
        } catch (RuntimeException ex) {
            mine.completeExceptionally(ex);
            throw ex;
        } finally {
            inflight.remove(key, mine);
        }
    }
}
```

Measured: Redis rps fell from 180k to 31k; origin rps fell 44%.

**Fix 3: hot-key sharding for the 41,000-key table.** One account table
accounted for 11% of all Redis CPU. Sharding it 64 ways moved it to a
per-shard load that no longer saturates a core.

```java
/**
 * The correctness cost, stated: sharded sub-copies can drift, so reads take
 * the highest version across shards. This converges if writes are monotonic
 * (they are: a version sequence). It does NOT converge if a shard write fails
 * permanently, so writes are retried and a shard repair job compares versions
 * across shards and repairs drift.
 *
 * Alternative considered and rejected: promoting the key to a local node.
 * Rejected because a single node becomes a single point of failure for the
 * hottest data, which is the opposite of what the cache is for.
 */
public final class ShardedAccountCache {
    public AccountSnapshot get(String accountId) {
        int base = Math.floorMod(murmur3(accountId), SHARDS);
        Map<Integer, AccountSnapshot> parts = new EnumMap<>(Integer.class);
        for (int i = 0; i < SHARDS; i++) {
            AccountSnapshot s = redis.get(key(accountId, i));
            if (s != null) parts.put((base + i) % SHARDS, s);
        }
        return parts.values().stream()
                .max(Comparator.comparingLong(AccountSnapshot::version))
                .orElse(null);
    }
}
```

**Fix 4: pull-based versioned invalidation.** Broadcast invalidation to 48
nodes on a write is an O(48) operation on the write hot path. The alternative
is a version counter that readers check.

```java
/**
 * Invalidation model, chosen for a write-heavy entity:
 *
 *   write path : bump a version key (one Redis INCR, ~0.2ms). No fan-out.
 *   read path  : local TTL bounds staleness; version is checked on the
 *                Redis read we are making anyway (a pipeline, not a round trip)
 *   guarantee   : bounded by max(localTTL, globalTTL) = 5s for accounts
 *
 * The trade: a change is visible up to 5s late. That is acceptable because the
 * same staleness already exists at the read replica, so the cache is not the
 * weakest link in the chain.
 */
public void invalidate(String entityId) {
    redis.incr(versionKey(entityId));
    localCache.invalidate(entityId);              // best-effort, same-pod only
}
```

## Measured outcomes

| Metric | Before | After |
|---|---|---|
| Global hit rate | 61% | 92% |
| Effective hit rate incl. local | 61% | 97% |
| Redis rps peak | 180k | 31k |
| Origin rps (misses) | 79k | 5.6k |
| Origin p99 | 840ms | 61ms |
| Service p99 | 410ms | 38ms |
| Memory used | 3.2TB of 1.4TB RAM (evicting) | 890GB |
| Cache-miss origin failure → outage | 4 min became 40 min | 4 min stayed 4 min |
| Stampede events per month | 9 | 0 |

The last two rows are the ones that matter more than the latency. The latency
improvement is a performance win; the stampede elimination is an availability
win.

## Failure Modes and the Runbook

1. **Origin outage with a cold cache.** Symptom: every request misses and the
   origin is overwhelmed, extending the outage. Fix: local cache with
   coalescing, plus a circuit breaker that serves stale local data with a
   freshness warning header rather than blocking on the origin.
2. **Hot key saturates one shard.** Symptom: p99 on one shard only. Fix:
   hot-key detection (per-key rps), then sharding; the detection is the
   durable part, because the next hot key will appear.
3. **Key schema change loses the cache.** Symptom: hit rate drops to zero on a
   deploy. Fix: version the key prefix (`v3:account:{id}`) and keep the old
   prefix readable for a TTL window so a rollback is instant.
4. **Memory exhaustion from a TTL regression.** Symptom: evictions spike, hit
   rate falls. Fix: an eviction-rate SLO, per-key-class memory budgets, and a
   CI test that asserts each key class has a TTL.
5. **Shard drift after a failed sharded write.** Symptom: some reads see an
   older account version. Fix: the repair job comparing versions across
   shards; writes are retried and a permanently failed shard write is a page.
6. **PCI scope creep.** Symptom: the cache enters PCI scope because it holds
   cardholder data. Fix: never cache PAN/CVV — cache a token; the scope
   exclusion is documented and re-verified at each annual assessment.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Redis Cluster distributes data across hash slots and provides replication;
  slot-level sharding is why a single hot key can saturate a node, and why
  key distribution matters.
  - Reference: https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/
  - Reference: https://redis.io/docs/latest/operate/oss_and_stack/reference/eviction/
- Redis pipelining batches commands into one round trip, which is the
  mechanism for making a read-plus-version-check a single network operation.
  - Reference: https://redis.io/docs/latest/develop/use/pipelining/
- Caching-aside with TTL and a short local layer, plus coalescing concurrent
  loads of the same key, is the standard defence against a stampede; the
  transactional outbox / idempotent-consumer pattern is the related defence on
  the event side.
  - Reference: https://redis.io/docs/latest/develop/use/pubsub/
  - Reference: https://microservices.io/patterns/data/transactional-outbox.html

## Deliverables
- [ ] Hit-rate root-cause analysis with the 5 causes and their contributions
- [ ] TTL tier policy aligned to downstream staleness budgets
- [ ] Per-pod local cache with single-flight, sized and measured
- [ ] Bloom filters in front, with false-positive rate and memory accounting
- [ ] Hot-key sharding for the 41,000-key table, with the convergence argument
- [ ] Pull-based versioned invalidation, with a stated staleness guarantee
- [ ] Circuit breaker serving stale local data with a freshness header
- [ ] Key schema versioning for cache-preserving deploys and rollbacks
- [ ] PCI scope exclusion documented (no PAN/CVV in the cache)
- [ ] Runbook for the six failure modes
