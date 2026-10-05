# Consistency Models - Mini Project

## Project: A Session-Consistent Shopping Cart

### Objective
Build a cart backed by three replicas and implement four consistency models against the
same interface, then measure the latency you traded and the anomaly each one permits.

### Requirements
1. `Replica` — local map plus an eventually converging push channel
2. `ConsistencyLevel` interface with four implementations
3. `StrongConsistency` (quorum R+W > N), `ReadYourWrites` (session-tracked token),
   `MonotonicReads` (stick to one replica per session), `EventualConsistency`
4. `ConsistencyHarness` that runs concurrent writers and readers and records anomalies
5. JUnit tests that reproduce each anomaly deterministically

### Steps

**Step 1: Replica and push channel**
```java
final class Replica {
    private final String id;
    private final ConcurrentMap<String, CartLine> lines = new ConcurrentHashMap<>();
    private final BlockingQueue<Mutation> inbox = new LinkedBlockingQueue<>();

    void apply(Mutation m) {  // must be commutative-safe
        lines.compute(m.sku(), (k, old) ->
            old == null || m.version() > old.version() ? m.line() : old);
    }
    Optional<CartLine> localRead(String sku) { return Optional.ofNullable(lines.get(sku)); }
}
```
Versioned last-writer-wins apply means out-of-order delivery cannot corrupt a replica.

**Step 2: Four levels, one interface**
```java
interface ConsistencyLevel {
    CartLine read(Store s, Session sess, String sku);
    void      write(Store s, Session sess, CartLine line);
}
```
- `StrongConsistency.read` — read W replicas, return the highest version, require W > N/2
- `ReadYourWrites.read` — if `sess.lastWriteVersion().containsKey(sku)`, block until that
  version is visible; otherwise fall through to monotonic read
- `MonotonicReads.read` — pin the replica in `sess.pinnedReplica`; if it is down, fail over
  and reset the session
- `EventualConsistency.read` — read any single replica, return whatever it has

**Step 3: Build the harness**
```java
@Test
void readYourWritesNeverRegresses() {
    harness.run(session -> {
        var line = new CartLine("SKU-1", 3, 1L);
        write(session, line);              // version bumps
        var seen = read(session, "SKU-1"); // must be >= 3, not the pre-write value
        assertThat(seen.quantity()).isGreaterThanOrEqualTo(3);
    });
}
```
Run each test 1000 iterations with an injected delay; the eventual-consistency test is
*expected* to fail, which is the point — paste the failure into the write-up.

**Step 4: Measure the trade**
Record p50/p99 read latency per level at N=3 and W=2/3. Strong consistency should be
measurably slower; write the numbers, do not assert them from memory.

**Step 5: Write the anomaly table**

| Model | Anomaly it permits | Cost paid |
|---|---|---|
| Strong | none (linearizable) | highest read latency |
| Read-your-writes | session sees another user's fresh write as stale | one extra round trip on miss |
| Monotonic reads | new replica may return older value after failover | sticky-replica coupling |
| Eventual | arbitrary stale read, write lost on all replicas | lowest latency |

### Deliverables
1. `Store`, `Replica`, `Session`, four `ConsistencyLevel` implementations
2. `ConsistencyHarness` with per-level latency percentiles
3. Four tests, one per model, including the deliberately failing eventual test
4. A one-page decision: which level each cart endpoint should use and why

### Extension (CHALLENGE)
Add `MonotonicReads` + failover and show the session silently regressing when the pinned
replica is replaced — then add a session epoch to detect it.

### Estimated Time
3-4 hours