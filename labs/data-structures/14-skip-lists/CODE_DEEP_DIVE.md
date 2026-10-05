# Code Deep Dive: Skip Lists

Core idea: A skip list layers sorted linked lists with geometrically-distributed tower heights, giving expected O(log n) ops with simple lock-friendly code.

## Class overview

Single class under `src/` exposing the contract table from THEORY; every public method restores all invariants before returning.

## Key fields

```java
// invariant: level-0 chain is fully sorted
// (see THEORY for the full invariant list)
private int size; // maintained on every path, incl. delete
```

- level-0 chain is fully sorted
- tower of key k is contiguous from level 0 up
- head has MAX_LEVEL sentinels (-inf)
- expected height of n towers is O(log n)

## Reference skeleton (fill in the bodies)

```java
public final class LabStructure {
    public LabStructure(/* capacity / params */) { /* empty-state invariant */ }
    public void op0(/* args */) { /* search(k) [E[O(log n)]] */ }
    public void op1(/* args */) { /* insert(k,v) [E[O(log n)]] */ }
    public void checkInvariants() { /* throw AssertionError on violation */ }
    @Override public String toString() { /* ASCII dump for traces */ return ""; }
}
```

## Hot path: `search(k)`

```java
// search(k): top-down, forward while next.key < k [E[O(log n)]]
public void hotPath(/* args */) {
    // 1. handle empty / singleton fast paths
    // 2. walk the structure touching O(bound) nodes
    // 3. restore bookkeeping (counts / tags / parents)
    // 4. assert checkInvariants() in debug builds
}
```

Trace it: run two multi-step scenarios by hand and assert the ASCII dump matches.

## Second op: `insert(k,v)`

```java
// insert(k,v): random level + splice at each layer [E[O(log n)]]
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

- `search(k)`: E[O(log n)] - top-down, forward while next.key < k
- `insert(k,v)`: E[O(log n)] - random level + splice at each layer
- `delete(k)`: E[O(log n)] - splice out at all layers
- `randomLevel()`: O(1) - coin flips, p=1/2 capped at MAX
- `rangeScan(a,b)`: O(log n + m) - level-0 walk between bounds
- `size()`: O(1) - maintained counter

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
