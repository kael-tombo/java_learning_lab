# Distributed Caching (Deep) - Mini Project

## Project: Coherence Under Adversarial Invalidation

### Objective
Build a multi-node cache with two invalidation protocols, inject the specific races each
protocol fails on, and add the defences until staleness is provably bounded.

### Requirements
1. `CacheClient` — cache-aside, single-flight, negative caching, stale-while-revalidate
2. `CacheAsideStrategy` and `WriteThroughStrategy` behind one interface
3. `WriteBehindCache` with a durable flush queue and bounded staleness accounting
4. `CoherenceHarness` — concurrent writers/readers plus invalidation message loss injection
5. Tests asserting a *bounded* staleness window, not zero staleness

### Steps

**Step 1: Single-flight is not optional**
```java
Product get(String sku) {
    var entry = local.get(sku);
    if (entry != null) return entry.maybeStale(origin::fetch);

    return flights.computeIfAbsent(sku, k -> {
        var fresh = origin.fetch(k);
        if (fresh == null) local.put(k, Entry.negative(ttlNegative));  // penetration defence
        else local.put(k, Entry.of(fresh, ttlFor(fresh)));
        return fresh;
    }).join();
}
```
A `ConcurrentHashMap<String, CompletableFuture<T>>` is all it takes. Without it, one expired
hot key produces one origin fetch per concurrent reader.

**Step 2: Invalidation protocol A — delete on write**
```java
void onProductUpdated(Product p) {
    origin.write(p);
    broadcast(new Invalidate(p.sku()));       // best effort, no ordering, no retries
}
```
Failure mode: a reader that has *already fetched* old data writes it into its local cache
**after** the invalidation arrives. The invalidation is now lost forever and the stale value
sits until TTL.

```java
@Test
void deleteOnWriteLosesToAStaleFill() {
    var read = client.beginGet("SKU-1");      // fetches v1, pauses before caching
    invalidate("SKU-1");                      // arrives and deletes nothing
    read.completeWith(v1);                    // now caches v1 -- stale, forever
    assertThat(client.get("SKU-1").version()).isEqualTo(1);   // the bug, demonstrated
}
```
That test is the single most useful thing you will write in this lab.

**Step 3: Invalidation protocol B — versioned keys**
```java
void onProductUpdated(Product p) {
    origin.write(p);
    meta.set("version:SKU-1", p.version());   // monotonic, separate from the payload
}
Product get(String sku) {
    var v = meta.get("version:" + sku);
    var key = "SKU-1@" + v;                   // version is IN the key
    var hit = local.get(key);
    if (hit != null) return hit;
    var p = origin.fetch(sku);
    local.put(key, p);                        // old key is now simply unreachable
    return p;
}
```
No deletion required. A stale reader writes to the *old* key, which nobody looks up again.
Coherence is now a property of the key space, not of message delivery — much stronger, and
it costs metadata reads and extra keys.

**Step 4: Stale-while-revalidate**
```java
Product get(String sku) {
    var entry = local.get(sku);
    if (entry == null) return blockingFetch(sku);
    if (entry.isFresh()) return entry.value();
    if (entry.isWithinGrace()) { revalidateAsync(sku); return entry.value(); }  // serve, refresh
    return blockingFetch(sku);
}
```
Promote-day insurance: a slightly stale catalogue beats a 503. The grace window is a
business decision, and you must write down its length.

**Step 5: Write-behind with durability accounting**
```java
void put(String sku, Product p) {
    local.put(sku, p);
    dirtyQueue.offer(sku);                    // coalesce: many writes, one flush
}
void flush() {
    for (var sku : dirtyQueue.drain()) {
        var v = local.get(sku);
        origin.write(sku, v);
        flushedAt.put(sku, now);               // staleness clock starts at flush, not write
    }
}
```
Track `now - flushedAt` per key and expose it as a metric. When that metric exceeds the
business tolerance, you have a real incident — and you now have the number to prove it.

**Step 6: Bounded-staleness test suite**
```java
@ParameterizedTest
void stalenessNeverExceedsTtl(invalidationProtocol, ttl) {
    harness.runWithRandomInvalidationLoss(writer, reader, ttl);
    assertThat(harness.maxObservedStaleness()).isLessThanOrEqualTo(ttl);
}
```
You cannot prove zero staleness with delete-on-write. You *can* prove staleness ≤ TTL with
TTL as the backstop. Aim the assertion at the guarantee you actually made.

### Deliverables
1. `CacheClient`, `CacheAsideStrategy`, `WriteThroughCache`, `WriteBehindCache`
2. The stale-fill race test that demonstrates protocol A's failure
3. Versioned-key implementation with the same test passing
4. Stale-while-revalidate with a configurable grace window and a max-staleness metric

### Extension (CHALLENGE)
Add a local in-process cache in front of the distributed one and measure how much of the
stampede the L1 absorbs — then show the L1 invalidation lag becoming the dominant staleness
source.

### Estimated Time
4 hours