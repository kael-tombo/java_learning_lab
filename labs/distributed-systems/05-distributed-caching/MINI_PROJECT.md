# Distributed Caching - Mini Project

## Project: A Product-Catalogue Cache That Survives a Flash Sale

### Objective
Build a multi-node product cache with consistent-hash placement, then load it with a hot
key and prove the stampede — and fix it.

### Requirements
1. `ConsistentHashRing` with virtual nodes for even key distribution
2. `DistributedCache` — cache-aside with TTL and negative caching
3. `SingleFlight` loader: exactly one origin fetch per missing key, concurrent waiters share
4. `WriteBehindCache` with a bounded flush queue
5. `StampedeHarness` driving N threads at one key and counting origin calls

### Steps

**Step 1: Consistent hashing with virtual nodes**
```java
Map<Long, Node> ring() {
    var tree = new TreeMap<Long, Node>();
    for (var node : nodes)
        for (int i = 0; i < VIRTUAL_NODES; i++)
            tree.put(hash(node.id() + "#" + i), node);
    return Map.copyOf(tree);
}
Node ownerOf(String key) { return ring.ceilingEntry(hash(key)).orElse(ring.firstEntry()).getValue(); }
```
With 3 nodes and no virtual nodes, key distribution is lumpy; with 150 per node it evens
out. Add a test that asserts max-load / min-load ratio < 1.5 across 10k keys — otherwise
rebalancing will be an outage.

**Step 2: Cache-aside with single-flight**
```java
Product get(String sku) {
    var hit = cache.get(sku);
    if (hit != null) return hit.value();               // may be NEGATIVE sentinel

    return flights.computeIfAbsent(sku, skuKey -> {
        var p = origin.fetch(skuKey);                  // exactly one thread runs this
        cache.put(skuKey, new Entry(p, ttlFor(p)));
        if (p == null) cache.put(skuKey, NEGATIVE);   // negative caching
        return p;
    }).join();
}
```
Both single-flight and negative caching are load-bearing. Without negative caching, a scan
for nonexistent SKUs misses 100% of the time and origin falls over.

**Step 3: Reproduce the stampede**
Remove single-flight, set the hot key's TTL to 1 second, and drive 500 concurrent readers:
```java
@Test
void withoutSingleFlightOriginIsStormed() {
    cache.clear();
    IntStream.range(0, 500).parallel()
        .forEach(i -> cache.get("HOT-SKU"));
    assertThat(origin.callCount("HOT-SKU")).isGreaterThan(50);  // observe the storm
}
```
Record the number. Then re-enable single-flight and assert it drops to 1. That delta is the
entire argument.

**Step 4: Write-behind, and its data-loss window**
```java
void put(String sku, Product p) {
    local.put(sku, p);                       // visible immediately
    queue.offer(new Dirty(sku, p));          // async to origin
}
void flush() {
    for (var d : queue.drain()) {
        origin.write(d.sku(), d.value());
        queue.ack(d);                        // ack AFTER write, never before
    }
}
```
Kill the process between `local.put` and the origin write. The value is lost forever. Write
the failure down honestly and note when this trade is acceptable (metrics, view counts) and
when it is not (balances, orders).

**Step 5: Break the cache key deliberately**
Ship a version change: `product:v1:{sku}` → `product:v2:{sku}`. Show that the old key is now
unreferenced memory, and that without a version prefix every deploy is a cache-wide purge.

### Deliverables
1. `ConsistentHashRing`, `DistributedCache`, `SingleFlight`, `WriteBehindCache`
2. Load-distribution test (ratio < 1.5) and stampede test (origin calls = 1)
3. A measured before/after origin-call count under 500-thread load
4. A short write-up: TTL policy per key type and the write-behind data-loss window

### Extension (CHALLENGE)
Implement request coalescing across *processes* using a cache-level distributed lock, then
show what happens when the lock holder dies mid-fetch.

### Estimated Time
3-4 hours