# CAP Theorem - Mini Project

## Project: A Replicated KV Store You Can Break

### Objective
Build a two-node key-value store where consistency is a configurable choice, then prove
the CAP theorem by pulling the network cable yourself.

### Requirements
1. Two `Node` instances communicating over a toggleable `Link`
2. `ConsistencyMode` enum: `CP` (quorum read/write) and `AP` (last-write-wins, async replicate)
3. `PartitionSimulator` that can sever and heal a link at runtime
4. A driver that writes through node A, partitions, writes through node B, then reads both
5. JUnit test asserting the exact divergence each mode produces

### Steps

**Step 1: Skeleton**
```java
public final class Node {
    private final String id;
    private final Map<String, VersionedValue> store = new ConcurrentHashMap<>();
    private Link link;

    Optional<VersionedValue> read(String key) { return Optional.ofNullable(store.get(key)); }
    void write(String key, String value, long lamport, String origin) {
        store.put(key, new VersionedValue(value, lamport, origin));
        link.replicate(key, store.get(key));
    }
}
```
`VersionedValue` carries `(value, lamport, origin)` — LWW merge compares `lamport`, then
breaks ties on `origin` so both nodes reach the same answer.

**Step 2: The kill switch**
```java
public final class Link {
    private volatile boolean up = true;
    void replicate(String key, VersionedValue v) {
        if (!up) { dropped.increment(); return; }   // replication silently lost
        peer.write(key, v, ...);
    }
    void partition() { up = false; }
    void heal()    { up = true;  fullResync(); }   // naive full-state resync
}
```
Never let `replicate` throw. A partition is not an exception; it is a lost message.

**Step 3: Run the three scenarios**

| Scenario | CP mode | AP mode |
|---|---|---|
| No partition | converged, linearizable | converged |
| Partitioned, write to A then read B | `UNAVAILABLE` | stale or new value, never error |
| Healed after LWW writes | converged | converged |

**Step 4: Assert the divergence**
```java
@Test
void cpModeRefusesStaleReadAcrossPartition() {
    cluster.partition();
    cluster.write("a", "one");
    cluster.write("b", "two");          // second node, quorum unreachable

    assertThat(cluster.readThroughBoth()).allMatch(r -> r.isPresent());
    // CP: at least one node must reject rather than answer
}
```

**Step 5: Measure the trade**
Count `dropped` messages and count rejected reads. Plot availability against consistency
for both modes — the curve you draw is the theorem.

### Deliverables
1. `Node`, `Link`, `ConsistencyMode`, `PartitionSimulator` in `com.distributed.cap`
2. Test class proving CP rejects and AP serves stale
3. A one-page table of which guarantee each mode surrenders under partition
4. A short note on PACELC: what happens *elsewhere* when there is no partition

### Extension (CHALLENGE)
Add a third mode, `PACELC_AVAILABLE`, that trades consistency for latency in the normal
(no-partition) case, and measure the p99 you traded away.

### Estimated Time
2-3 hours