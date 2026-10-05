# Code Deep Dive: Concurrent Data Structures

Core idea: Concurrent structures trade single-thread speed for linearizable multi-threaded behavior via fine-grained locks, lock-free CAS loops, or immutability.

## Class overview

Single class under `src/` exposing the contract table from THEORY; every public method restores all invariants before returning.

## Key fields

```java
// invariant: every published reference is safely constructed (final/volatile)
// (see THEORY for the full invariant list)
private int size; // maintained on every path, incl. delete
```

- every published reference is safely constructed (final/volatile)
- lock ordering is global to avoid deadlock
- CAS loops always re-read before retry
- iterators are weakly consistent, never fail-fast

## Reference skeleton (fill in the bodies)

```java
public final class LabStructure {
    public LabStructure(/* capacity / params */) { /* empty-state invariant */ }
    public void op0(/* args */) { /* cas(addr,exp,new) [lock-free] */ }
    public void op1(/* args */) { /* putIfAbsent(k,v) [~O(1)] */ }
    public void checkInvariants() { /* throw AssertionError on violation */ }
    @Override public String toString() { /* ASCII dump for traces */ return ""; }
}
```

## Hot path: `cas(addr,exp,new)`

```java
// cas(addr,exp,new): atomic compare-and-set retry loop [lock-free]
public void hotPath(/* args */) {
    // 1. handle empty / singleton fast paths
    // 2. walk the structure touching O(bound) nodes
    // 3. restore bookkeeping (counts / tags / parents)
    // 4. assert checkInvariants() in debug builds
}
```

Trace it: run two multi-step scenarios by hand and assert the ASCII dump matches.

## Second op: `putIfAbsent(k,v)`

```java
// putIfAbsent(k,v): ConcurrentHashMap atomic insert [~O(1)]
public void secondOp(/* args */) {
    // mirror the hot path structure; share helpers, not copy-paste
    // every early return still restores invariants
}
```

## Pitfalls (Java-specific)

- `==` vs `.equals` on keys; broken `hashCode` contracts.
- Overflow in mid/size math: `lo + ((hi - lo) >>> 1)`, `long` accumulators.
- 1-based vs 0-based slips; half-open `[l, r)` discipline everywhere.
- Stale auxiliary state on delete paths (counts, tags, parents).
- Recursive depth on skewed input; prefer iterative with explicit stack.
- Leaking mutable internals; defensive copies or unmodifiable views.

## Complexity audit

- `cas(addr,exp,new)`: lock-free - atomic compare-and-set retry loop
- `putIfAbsent(k,v)`: ~O(1) - ConcurrentHashMap atomic insert
- `stripedAdd(x)`: O(1) contended - LongAdder cell hashing
- `copyOnWrite()`: O(n) write / O(1) read - snapshot array on mutation
- `drainTo(queue)`: O(m) - bulk transfer under minimal lock
- `sizeEstimate()`: O(stripes) - summed striped counters

## Testing plan (JUnit 5)

- Empty, singleton, boundary, duplicates, adversarial order.
- Property test: random ops vs a naive model (TreeMap/ArrayList) for 10k steps.
- Invariant check after every single op in fuzz mode.
- Benchmark: `System.nanoTime` with warmup, 5 measured runs, report ns/op.

## Review checklist

- [ ] Every public method restores invariants on all return paths.
- [ ] No hidden linear scans inside a claimed sublinear op.
- [ ] Overflow, indexing, and aliasing pitfalls addressed with tests.
- [ ] ASCII dump output matches the committed hand traces.
