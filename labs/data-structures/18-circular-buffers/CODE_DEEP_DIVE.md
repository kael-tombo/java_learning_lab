# Code Deep Dive: Circular (Ring) Buffers

Core idea: A ring buffer maps logical sequence numbers to array slots modulo capacity; head/tail cursors give O(1) enqueue/dequeue with zero allocation.

## Class overview

Single class under `src/` exposing the contract table from THEORY; every public method restores all invariants before returning.

## Key fields

```java
// invariant: 0 <= size <= capacity always
// (see THEORY for the full invariant list)
private int size; // maintained on every path, incl. delete
```

- 0 <= size <= capacity always
- slot index = sequence & (cap-1) for power-of-2 caps
- SPSC: only producer writes tail, only consumer writes head
- full vs empty disambiguated by size count, not head==tail alone

## Reference skeleton (fill in the bodies)

```java
public final class LabStructure {
    public LabStructure(/* capacity / params */) { /* empty-state invariant */ }
    public void op0(/* args */) { /* offer(x) [O(1)] */ }
    public void op1(/* args */) { /* poll() [O(1)] */ }
    public void checkInvariants() { /* throw AssertionError on violation */ }
    @Override public String toString() { /* ASCII dump for traces */ return ""; }
}
```

## Hot path: `offer(x)`

```java
// offer(x): write at tail if not full [O(1)]
public void hotPath(/* args */) {
    // 1. handle empty / singleton fast paths
    // 2. walk the structure touching O(bound) nodes
    // 3. restore bookkeeping (counts / tags / parents)
    // 4. assert checkInvariants() in debug builds
}
```

Trace it: run two multi-step scenarios by hand and assert the ASCII dump matches.

## Second op: `poll()`

```java
// poll(): read at head if not empty [O(1)]
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

- `offer(x)`: O(1) - write at tail if not full
- `poll()`: O(1) - read at head if not empty
- `isFull()/isEmpty()`: O(1) - size vs capacity checks
- `size()`: O(1) - (tail-head) mod cap, careful with wrap
- `resize(cap)`: O(n) - drain into new power-of-2 array
- `peek()`: O(1) - non-destructive head read

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
