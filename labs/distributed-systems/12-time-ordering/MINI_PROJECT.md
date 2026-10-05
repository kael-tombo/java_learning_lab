# Time Ordering (Deep) - Mini Project

## Project: Causal Broadcast with a Version Vector Audit Trail

### Objective
Implement three broadcast layers — FIFO, total-order FIFO, and causal — send the same
concurrent message pattern through each, and record which invariants hold.

### Requirements
1. `EventClock` — wraps HLC with monotonicity guarantees per process
2. `CausalBroadcast` — per-process FIFO queue, deliver-after-deliver, holdback for gaps
3. `VectorClock` with dependency tracking and concurrent-edit detection
4. `BroadcastHarness` running the same scenario through each layer
5. Tests asserting the specific invariant each layer guarantees

### Steps

**Step 1: Hybrid logical clock, carefully**
```java
record Hlc(long physicalMillis, int logical, String nodeId) implements Comparable<Hlc> {
    public int compareTo(Hlc o) {
        int c = Long.compare(physicalMillis, o.physicalMillis);
        return c != 0 ? c : Integer.compare(logical, o.logical);
    }
}

Hlc now() {                                   // local event
    long phys = clock.millis();
    if (phys > h.physicalMillis()) h = new Hlc(phys, 0, id);
    else h = new Hlc(h.physicalMillis(), h.logical() + 1, id);
    return h;
}
Hlc receive(Hlc remote) {                     // handles the same-millisecond collision
    long phys = Math.max(clock.millis(), h.physicalMillis(), remote.physicalMillis());
    int log;
    if (phys == h.physicalMillis() && phys == remote.physicalMillis())
        log = Math.max(h.logical(), remote.logical()) + 1;
    else if (phys == h.physicalMillis()) log = h.logical() + 1;
    else if (phys == remote.physicalMillis()) log = remote.logical() + 1;
    else log = 0;
    h = new Hlc(phys, log, id);
    return h;
}
```
Note: `logical` must **overflow into `physicalMillis`**, not wrap. Clamp with
`Math.addExact` and carry.

**Step 2: FIFO — the baseline that fails**
```java
class FifoBroadcast {                        // guarantees only per-sender order
    void deliver(Message m) { queue.addLast(m); flush(); }
}
```
Scenario: process A sends `m1`, process B sends `m2` concurrently, B's `m2` reaches everyone
first. A user watching two processes can see `m2` then `m1` and conclude `m1` never happened.

**Step 3: Total-order FIFO — ordered, not causal**
Impose a total order via a sequencer (or HLC comparison). All processes see the same order,
so no divergence — but total order is *stronger than causality and needlessly so*. Point out
that it forces unrelated concurrent events into an arbitrary sequence, which is fine for
consistency and wrong for understanding intent.

**Step 4: Causal broadcast — deliver-after-deliver**
```java
class CausalBroadcast {
    private final Map<String, Queue<Message>> holdback = new HashMap<>();
    private final Set<String> deliveredIds = new HashSet<>();
    private final Deque<Message> pending = new ArrayDeque<>();

    void receive(Message m) { pending.addLast(m); drain(); }

    private void drain() {
        boolean progress = true;
        while (progress) {
            progress = false;
            for (var it = pending.iterator(); it.hasNext(); ) {
                var m = it.next();
                if (!deliveredIds.contains(m.id()) && dependenciesDelivered(m)) {
                    it.remove(); deliver(m); deliveredIds.add(m.id()); progress = true;
                } else if (!dependenciesSatisfied(m)) {
                    holdback.computeIfAbsent(m.from(), k -> new ArrayDeque<>()).add(m);
                    it.remove(); progress = true;
                }
            }
        }
    }
}
```
`dependenciesDelivered` checks the sender's own sequence: every earlier message from the
same sender must already be delivered. FIFO per sender, plus never deliver X before Y when
Y happened-before X.

**Step 5: Version vectors and concurrent edits**
```java
boolean concurrent(Map<String,Integer> a, Map<String,Integer> b) {
    boolean aAhead = a.entrySet().stream().anyMatch(e -> e.getValue() > b.getOrDefault(e.getKey(), 0));
    boolean bAhead = b.entrySet().stream().anyMatch(e -> e.getValue() > a.getOrDefault(e.getKey(), 0));
    return aAhead && bAhead;
}
```
Two offline clients edit the same field concurrently. A total order picks a winner and loses
one edit; a CRDT merge keeps both. Show the difference and name the domain cost of each.

### Deliverables
1. `EventClock`, `FifoBroadcast`, `TotalOrderBroadcast`, `CausalBroadcast`
2. One test per layer asserting its exact guarantee, plus the test each *fails*
3. Vector-clock concurrent-edit detector with a merge demonstration
4. An invariant table: which layer guarantees what, at what cost

### Extension (CHALLENGE)
Bound the delivered-ID set (a sliding window per sender) so memory is constant, then show
what breaks when the window is too small and prove the window size requirement.

### Estimated Time
4 hours