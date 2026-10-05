# Distributed Cache — MINI PROJECT

## Project: Sharded Cache with Consistent Hashing, TinyLFU, and Single-Flight

A working distributed cache in a single JVM with simulated nodes: consistent
hashing for placement, TinyLFU admission with LRU eviction, single-flight
loading, hot-key sharding, and a metrics layer.

### Scope
- Consistent hash ring with 150 virtual nodes per physical node, with a resize
  simulation that reports the remapping fraction.
- Eviction: segmented LRU + frequency sketch admission (TinyLFU style).
- Single-flight: concurrent misses on the same key trigger one origin load.
- Hot-key sharding: N sub-shards behind one logical key, with a read fan-in.
- TTL + versioned invalidation, with a per-key "invalidation epoch" option.
- Metrics: hits, misses, loads, evictions, admissions rejected, load latency.

### Architecture

```
 client -> [consistent hash ring] -> shard -> [segmented LRU + TinyLFU admission]
                                        |
                                  miss -> [single-flight group] -> origin
                                        |
                                  hot key -> [N sub-shards, one owner each]
```

### Implementation — consistent hashing

```java
public final class ConsistentHashRing {
    private final int virtualNodes;
    private final NavigableMap<Long, String> ring = new TreeMap<>();
    private final Map<String, List<String>> replicas = new HashMap<>();

    public ConsistentHashRing(Collection<String> nodes, int virtualNodes) {
        this.virtualNodes = virtualNodes;
        nodes.forEach(this::addNode);
    }

    public void addNode(String node) {
        for (int i = 0; i < virtualNodes; i++) {
            String vnode = node + "#" + i;
            ring.put(murmur3(vnode), vnode);
        }
        replicas.computeIfAbsent(node, k -> new ArrayList<>())
                .addAll(List.of(node + "#" + 0));
    }

    public void removeNode(String node) {
        String prefix = node + "#";
        ring.entrySet().removeIf(e -> e.getValue().startsWith(prefix));
    }

    /** clockwise lookup, the first vnode at or after the key's hash */
    public List<String> owners(String key, int replicaCount) {
        if (ring.isEmpty()) return List.of();
        long h = murmur3(key);
        var tail = ring.tailMap(h, true);
        var it = tail.isEmpty() ? ring.entrySet().iterator() : tail.entrySet().iterator();
        List<String> out = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        while (out.size() < replicaCount && it.hasNext()) {
            String vnode = it.next().getValue();
            String physical = vnode.substring(0, vnode.indexOf('#'));
            if (seen.add(physical)) out.add(physical);
        }
        return out;
    }
}
```

Virtual nodes are not decoration: with 1 vnode per node, adding a node remaps
roughly `1/n` of keys but with high variance. With 150, the remap is smooth and
predictable, which is what makes a rolling resize safe.

```java
/** The test that justifies virtual nodes: remap fraction on resize. */
public record ResizeResult(int before, int after, long remapped, double remapFraction) {
    public boolean acceptable() { return remapFraction < 0.20; }
}

public ResizeResult simulateResize(Set<String> keys, List<String> before,
                                   List<String> after, int replicas) {
    ConsistentHashRing r1 = new ConsistentHashRing(before, 150);
    ConsistentHashRing r2 = new ConsistentHashRing(after, 150);
    long moved = keys.stream()
            .filter(k -> !r1.owners(k, replicas).equals(r2.owners(k, replicas)))
            .count();
    return new ResizeResult(before.size(), after.size(), moved, (double) moved / keys.size());
}
```

### Implementation — TinyLFU admission

Pure LRU is destroyed by a scan: 1M unique keys evict the working set and the
hit rate collapses. Admission filters those out.

```java
public final class SegmentedCache {
    private final Segment[] segments;
    private final int perSegment;

    public SegmentedCache(int segments, int perSegment, int sketchSize) {
        this.segments = new Segment[segments];
        for (int i = 0; i < segments; i++) {
            segments[i] = new Segment(perSegment, new CountMinSketch(sketchSize));
        }
    }

    public V get(K key) {
        Segment s = segmentFor(key);
        Entry e = s.map.get(key);
        s.sketch.increment(key);            // record the access, hit or miss
        if (e == null) return null;
        if (e.expired()) { s.map.remove(key); return null; }
        s.lru.recordHit(key);
        return e.value;
    }

    public void put(K key, V value, Duration ttl) {
        Segment s = segmentFor(key);
        long candidateFreq = s.sketch.estimate(key);

        // TinyLFU admission: reject a newcomer if the victim is used more often.
        // One admission, not a promotion into a second structure.
        if (s.map.size() >= perSegment) {
            K victim = s.lru.leastRecentlyUsed();
            long victimFreq = s.sketch.estimate(victim);
            if (candidateFreq < victimFreq) {
                metrics.counter("admission.rejected").inc();
                return;                       // scan resistance: the scan loses
            }
            s.map.remove(victim);
            s.lru.remove(victim);
            metrics.counter("eviction").inc();
        }
        s.map.put(key, new Entry<>(value, now() + ttl.toMillis()));
        s.lru.recordUse(key);
    }

    private Segment segmentFor(K key) {
        // Hash to a segment, then a bounded LRU per segment. This caps the
        // worst-case eviction scan to one segment, not the whole cache.
        return segments[Math.floorMod(murmur3(key), segments.length)];
    }
}
```

### Implementation — single-flight

```java
public final class SingleFlight<K, V> {
    private final ConcurrentHashMap<K, CompletableFuture<V>> inflight = new ConcurrentHashMap<>();

    /**
     * The classic stampede: 5,000 requests for a key that just expired all miss
     * and all call the origin. Single-flight collapses them into one load and
     * the rest wait on the future. This is the single highest-value cache
     * feature for protecting a fragile origin.
     */
    public V load(K key, Function<K, V> loader) throws ExecutionException, InterruptedException {
        CompletableFuture<V> mine = new CompletableFuture<>();
        CompletableFuture<V> existing = inflight.putIfAbsent(key, mine);
        if (existing != null) {
            metrics.counter("singleflight.joined").inc();
            return existing.get();                    // wait for the leader
        }
        try {
            metrics.counter("singleflight.leader").inc();
            V v = loader.apply(key);
            mine.complete(v);
            return v;
        } catch (Throwable t) {
            mine.completeExceptionally(t);            // do not cache the failure
            throw t;
        } finally {
            inflight.remove(key, mine);                // always clear, even on failure
        }
    }
}
```

### Implementation — hot key sharding

```java
public final class HotKeyShardedCache {
    private final ConsistentHashRing ring;
    private final int shards;

    /**
     * Trade-off, stated explicitly: sharding a key means the sub-shards can
     * drift out of sync, so a read fan-in is only correct if the value is
     * immutable or versioned. With a version, reads return the highest version
     * seen, which converges. Without one, do not shard a mutable key.
     */
    public VersionedValue get(String key) {
        List<VersionedValue> parts = new ArrayList<>(shards);
        for (int i = 0; i < shards; i++) {
            String sub = key + "|" + i;
            String owner = ring.owners(sub, 1).get(0);
            parts.add(node(owner).getLocal(sub));
        }
        return parts.stream().filter(Objects::nonNull)
                .max(Comparator.comparingLong(VersionedValue::version))
                .orElse(null);
    }

    public void put(String key, Value value) {
        long version = versionSeq.incrementAndGet();
        for (int i = 0; i < shards; i++) {
            String sub = key + "|" + i;
            node(ring.owners(sub, 1).get(0))
                .putLocal(sub, new VersionedValue(value, version));
        }
    }
}
```

### The consistency contract, in writing

```java
/**
 * What this cache guarantees, precisely:
 *
 *   STRONG-ish : a read after a write on the same node returns the new value.
 *   EVENTUAL   : across replicas, convergence within `replicaLagMs`.
 *   AT-ONCE    : a value is never returned after its TTL.
 *   NOT        : monotonic reads, read-your-writes across nodes, or
 *                global invalidation ordering.
 *
 * Invalidation is pull-based, not broadcast: a version bump in the origin, and
 * each node checks the version on read (or on a short poll). Broadcast
 * invalidation is O(nodes) per write and becomes the bottleneck long before
 * the cache does.
 */
public record ConsistencyContract(Duration ttl, Duration replicaLag,
                                   boolean readYourWrites, boolean monotonicReads) {}
```

### Test It

```java
@Test void resizeRemapsOnlyTheMinimum() {
    Set<String> keys = IntStream.range(0, 100_000).mapToObj(i -> "k" + i).collect(toSet());
    ResizeResult r = simulateResize(keys, List.of("n1","n2","n3"), List.of("n1","n2","n3","n4"), 1);
    assertTrue(r.acceptable());
    assertEquals(0.25, r.remapFraction(), 0.08);   // 1 of 4 nodes: ~25%, low variance
}

@Test void scanDoesNotEvictTheWorkingSet() {
    SegmentedCache cache = new SegmentedCache(16, 1000, 10_000);
    for (int i = 0; i < 500; i++) { cache.get("hot" + i); cache.put("hot" + i, i, TTL); }  // working set
    for (int i = 0; i < 100_000; i++) cache.put("scan" + i, i, TTL);                          // scan
    long survived = IntStream.range(0, 500).filter(i -> cache.get("hot" + i) != null).count();
    assertTrue(survived > 400, "scan destroyed the working set: " + survived + "/500");
}

@Test void stampedeCollapsesToOneOriginCall() throws Exception {
    AtomicInteger originCalls = new AtomicInteger();
    ExecutorService pool = Executors.newFixedThreadPool(200);
    List<Future<?>> fs = new ArrayList<>();
    for (int i = 0; i < 200; i++) {
        fs.add(pool.submit(() -> flight.load("k", k -> { originCalls.incrementAndGet(); sleep(50); return "v"; })));
    }
    fs.forEach(f -> f.get());
    assertEquals(1, originCalls.get());
}
```

### Stretch
- Add a bloom-filter pre-check in front of the cache to skip misses entirely.
- Add a "negative caching" layer for known 404s with a short TTL.
- Benchmark LRU vs TinyLFU vs SLRU on a Zipf workload and plot hit rate over time.

## Deliverables
- [ ] Consistent hash ring with virtual nodes and a resize remap test
- [ ] Segmented cache with TinyLFU admission, scan-resistance benchmark
- [ ] Single-flight with a 200-thread stampede test
- [ ] Hot-key sharding with versioned fan-in reads and a stated correctness cost
- [ ] Written consistency contract enumerating what is and is not guaranteed
- [ ] Metrics: hits, misses, loads, evictions, admissions rejected, load latency
- [ ] Comparison benchmark: LRU vs TinyLFU vs SLRU
