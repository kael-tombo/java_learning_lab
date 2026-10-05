# Time and Ordering - Mini Project

## Project: Detecting Causality Violations in a Replicated Store

### Objective
Implement Lamport, vector, and hybrid logical clocks, then build a replica set where writes
arrive out of order and show which clock can detect the violation and which cannot.

### Requirements
1. `LamportClock` — counter with send/receive rules
2. `VectorClock` — per-node counters with compare and merge
3. `HybridLogicalClock` — physical time plus a logical counter
4. `Replica` accepting out-of-order writes and recording clock metadata
5. `CausalityAuditor` that flags writes arriving before their cause

### Steps

**Step 1: Lamport clocks — order without causality knowledge**
```java
void onSend()      { tick(); }
void onReceive(long remote) { value = max(value, remote) + 1; }
void tick()         { value++; }
```
`if (a < b) happens-before(a, b)`. The converse is **false**: `a > b` does not mean b
happened before a. Lamport gives total order, and that is all it gives.

**Step 2: Vector clocks — the information Lamport throws away**
```java
Map<String, Integer> vc = new HashMap<>();       // nodeId -> count

void onSend()   { vc.merge(local(), 1, Integer::sum); }
void onReceive(Map<String,Integer> remote) {
    vc = mergeComponentWiseMax(vc, remote);
    vc.merge(local(), 1, Integer::sum);
}
// null means concurrent; non-null is happened-before
Comparison compare(Map<String,Integer> other) {
    boolean anyLess = vc.entrySet().stream().anyMatch(e -> other.getOrDefault(e.getKey(),0) < e.getValue());
    boolean anyGreater = other.entrySet().stream().anyMatch(e -> vc.getOrDefault(e.getKey(),0) < e.getValue());
    if (anyLess && anyGreater) return CONCURRENT;
    return anyLess ? BEFORE : AFTER;
}
```
O(N) space per clock, and that cost is exactly what buys concurrency detection.

**Step 3: Build the anomaly**
Three nodes, a write chain A→B→C, then deliver C's write to A before B's:
```java
ca.write(w3);                      // C writes after receiving w2
a.receive(c.vectorOf(w3));         // arrives first
a.receive(b.vectorOf(w2));         // arrives second -- violates causality
assertThat(a.vector().compare(b.vectorOf(w2))).isEqualTo(BEFORE);   // detect it
```
Then show Lamport's verdict on the same sequence: it returns an order but no evidence that
the order was violated. That contrast is the lab's core lesson.

**Step 4: Hybrid logical clocks**
```java
HybridLogicalClock send() {
    long phys = clock.millis();
    if (phys > physical) { physical = phys; logical = 0; }
    else logical++;                          // same ms: bump logical, not physical
    return new Hlc(physical, logical, nodeId);
}
void onReceive(Hlc remote) {
    long phys = Math.max(clock.millis(), remote.physical, physical);
    if (phys == remote.physical && phys == physical) logical = Math.max(logical, remote.logical) + 1;
    else if (phys == remote.physical)        logical = remote.logical + 1;
    else if (phys == physical)               logical = logical + 1;
    else                                     logical = 0;
    physical = phys;
}
```
An HLC never goes backwards and stays within epsilon of physical time, which is what makes
it usable for both ordering and human-readable timestamps.

**Step 5: Physical clocks and why you avoid them**
Compute the max network delay (minimum RTT over many samples, one-way ≈ RTT/2) and build a
TrueTime-style interval `[earliest, latest]`. Show the interval width in your environment.
If the uncertainty exceeds your tolerance, you cannot build a correct lease on physical time
without GPS/PTP hardware.

### Deliverables
1. `LamportClock`, `VectorClock`, `HybridLogicalClock`, `TrueTime` interval estimator
2. Out-of-order delivery test proving vector clocks detect the violation
3. Side-by-side table: what Lamport vs vector vs HLC can and cannot determine
4. A measured interval width and the tolerance it implies

### Extension (CHALLENGE)
Add a logical clock to the outbox/consumer pipeline and prove that a consumer can detect
that it processed events out of causal order across two producers.

### Estimated Time
3-4 hours