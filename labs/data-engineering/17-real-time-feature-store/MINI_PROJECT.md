# Real-Time Feature Store — MINI PROJECT

## Project: Low-Latency Feature Serving Layer

An online feature store: sharded in-memory storage, batch and streaming updates,
per-feature TTLs, staleness-aware responses, and a documented fallback chain.

### Scope
- `FeatureStore`: sharded map store, `get(entity, features)` with p99 measurement.
- Update paths: batch upsert, streaming partial update, TTL per feature.
- Responses carry a per-feature `Freshness` marker the caller can act on.
- Fallback chain: online -> cache -> last-known-good -> model default.
- Load test: 50k reads/sec, report p50/p99 and memory per entity.

### Architecture

```
updates: batch job --------+
         streaming job -----+--> [FeatureStore, N shards]
                               |   entity -> {feature -> (value, writtenAt, ttl)}
reads:   serving API <-------+
         |
         +-- freshness metadata in the response
         +-- fallback chain: store -> local LRU -> last-known-good -> default
```

### Implementation

```java
public record FeatureValue(Object value, Instant writtenAt, Duration ttl, String source) {
    public boolean stale(Instant now) { return now.isAfter(writtenAt.plus(ttl)); }
    public long ageSeconds(Instant now) { return Duration.between(writtenAt, now).toSeconds(); }
    public Freshness freshness(Instant now) {
        if (stale(now)) return Freshness.STALE;
        long half = ttl.toSeconds() / 2;
        return ageSeconds(now) > half ? Freshness.AGING : Freshness.FRESH;
    }
}

public enum Freshness { FRESH, AGING, STALE, MISSING }
```

```java
public final class ShardedFeatureStore {
    private final Map<Integer, Shard> shards;
    private final int shardCount;

    public record Shard(Map<String, Map<String, FeatureValue>> rows,
                        ReentrantReadWriteLock lock) {
        public Shard {
            rows = new ConcurrentHashMap<>();
            lock = new ReentrantReadWriteLock();
        }
    }

    public ShardedFeatureStore(int shardCount) {
        this.shardCount = shardCount;
        Map<Integer, Shard> m = new HashMap<>();
        for (int i = 0; i < shardCount; i++) m.put(i, new Shard());
        this.shards = Map.copyOf(m);
    }

    /** FNV-1a: cheap, stable, no allocation. Hash stability across restarts
     *  matters more than avalanche quality for a sharded cache. */
    private int shardFor(String entityKey) {
        int h = 0x811c9dc5;
        for (int i = 0; i < entityKey.length(); i++) {
            h ^= entityKey.charAt(i);
            h *= 0x01000193;
        }
        return Math.floorMod(h, shardCount);
    }

    /**
     * Partial update: a streaming job that recomputes ONE feature must not
     * require re-sending the whole row, and a failure must not clear the rest.
     */
    public void upsert(String entityKey, Map<String, FeatureValue> updates) {
        Shard s = shards.get(shardFor(entityKey));
        s.lock().writeLock().lock();
        try {
            Map<String, FeatureValue> row =
                    s.rows().computeIfAbsent(entityKey, k -> new ConcurrentHashMap<>());
            updates.forEach(row::put);       // per-feature atomicity, not per-row
        } finally {
            s.lock().writeLock().unlock();
        }
    }

    public FeatureResponse get(String entityKey, List<String> features, Instant now) {
        Shard s = shards.get(shardFor(entityKey));
        s.lock().readLock().lock();
        try {
            Map<String, FeatureValue> row = s.rows().get(entityKey);
            Map<String, Object> values = new HashMap<>();
            Map<String, Freshness> freshness = new HashMap<>();
            for (String f : features) {
                FeatureValue fv = row == null ? null : row.get(f);
                if (fv == null) { freshness.put(f, Freshness.MISSING); continue; }
                values.put(f, fv.value());
                freshness.put(f, fv.freshness(now));
            }
            return new FeatureResponse(entityKey, values, freshness,
                    values.size() == 0 ? now : now);
        } finally {
            s.lock().readLock().unlock();
        }
    }
}
```

### Staleness-aware serving and fallback

```java
public record FeatureResponse(String entityKey, Map<String, Object> values,
                              Map<String, Freshness> freshness, Instant servedAt) {
    public boolean anyStale() { return freshness.values().stream()
            .anyMatch(f -> f == Freshness.STALE || f == Freshness.MISSING); }
}

public final class FeatureServer {
    private final ShardedFeatureStore store;
    private final Map<String, LocalLru> localCache;
    private final Map<String, Object> lastKnownGood;      // per entity, per feature
    private final Map<String, Object> modelDefaults;      // what the model can accept

    public Map<String, Object> serve(String entity, List<String> features, Instant now) {
        FeatureResponse primary = store.get(entity, features, now);
        Map<String, Object> out = new HashMap<>(primary.values());

        for (String f : features) {
            Freshness fr = primary.freshness().getOrDefault(f, Freshness.MISSING);
            if (fr == Freshness.FRESH) continue;

            Object fallback = switch (fr) {
                case AGING  -> localCache.get(f).get(entity);              // L1
                case STALE  -> lastKnownGood.get(entity + ":" + f);        // L2
                case MISSING -> modelDefaults.get(f);                     // L3
                default -> null;
            };
            if (fallback == null) {
                // Never invent a value. Say it is missing; the model decides.
                out.put(f, null);
                metrics.counter("feature.missing", f).inc();
            } else {
                out.put(f, fallback);
                metrics.counter("feature.fallback." + fr.name(), f).inc();
            }
        }
        return out;
    }
}
```

### The capacity model

```java
public record CapacityPlan(int entities, int featuresPerEntity,
                           int bytesPerValue, double replicationFactor,
                           double targetUtilization) {
    public long rawBytes() {
        return (long) entities * featuresPerEntity * bytesPerValue;
    }
    public long nodeBytes() {
        // Divide by replication and utilization, and round to a node size.
        return (long) Math.ceil(rawBytes() / (replicationFactor * targetUtilization));
    }
    public int nodes(long nodeCapacityBytes) {
        return (int) Math.ceil((double) nodeBytes() / nodeCapacityBytes);
    }

    public static CapacityPlan forRpsLatencyBudget() {
        // 90M entities x 24 features x 24 bytes ~= 51.7GB raw; at RF=2 and 70%
        // utilization that is ~74GB, so 3 nodes of 32GB with headroom.
        return new CapacityPlan(90_000_000, 24, 24, 2.0, 0.70);
    }
}
```

### Load test

```java
public record LatencyReport(long p50Micros, long p95Micros, long p99Micros,
                            long p999Micros, double throughputPerSec, double errorRate) {}

public LatencyReport loadTest(int threads, int seconds, List<String> features) {
    ExecutorService pool = Executors.newFixedThreadPool(threads);
    long deadline = System.nanoTime() + Duration.ofSeconds(seconds).toNanos();
    HdrHistogram recorder = new Recorder(3);
    AtomicLong reads = new AtomicLong(), errors = new AtomicLong();
    List<Future<?>> futures = new ArrayList<>();
    for (int t = 0; t < threads; t++) {
        futures.add(pool.submit(() -> {
            while (System.nanoTime() < deadline) {
                long t0 = System.nanoTime();
                try {
                    server.serve(entity(), features, Instant.now());
                    reads.incrementAndGet();
                } catch (Exception e) {
                    errors.incrementAndGet();
                }
                recorder.recordValue(System.nanoTime() - t0);
            }
        }));
    }
    futures.forEach(f -> { try { f.get(); } catch (Exception ignored) {} });
    pool.shutdown();
    return new LatencyReport(recorder.getValueAtPercentile(50) / 1000,
            recorder.getPercentileAtOrAbove(95) / 1000,
            recorder.getPercentileAtOrAbove(99) / 1000,
            recorder.getPercentileAtOrAbove(99.9) / 1000,
            reads.get() / (double) seconds, errors.get() / (double) reads.get());
}
```

### Test It

```java
@Test void partialUpdateKeepsOtherFeatures() {
    store.upsert("u1", Map.of("a", fv(1), "b", fv(2)));
    store.upsert("u1", Map.of("a", fv(9)));         // only 'a' recomputed
    var r = store.get("u1", List.of("a", "b"), now());
    assertEquals(9, r.values().get("a"));
    assertEquals(2, r.values().get("b"));          // untouched
}

@Test void staleFeatureUsesFallbackAndIsMarked() {
    store.upsert("u1", Map.of("x", new FeatureValue(1, now().minus(Duration.ofHours(2)),
            Duration.ofMinutes(15), "stream")));
    Map<String, Object> served = server.serve("u1", List.of("x"), now());
    assertEquals(lastKnownGood.get("u1:x"), served.get("x"));   // L2 fallback used
    assertTrue(server.lastResponseFreshness("u1").get("x") == Freshness.STALE);
}
```

### Stretch
- Add a delta update path: only changed features cross the wire.
- Add a hot-key guard: a burst on one entity degrades to a lock-free read path.
- Add shadow-mode comparison of old and new feature code paths.

## Deliverables
- [ ] Sharded store with FNV-1a routing and per-feature atomic updates
- [ ] Per-feature TTL with FRESH/AGING/STALE/MISSING freshness classification
- [ ] Three-level fallback chain that never invents a value
- [ ] Capacity model with a stated node count
- [ ] Load test reporting p50/p95/p99/p999 and throughput
- [ ] Test suite for partial update, expiry, fallback, and hot keys
