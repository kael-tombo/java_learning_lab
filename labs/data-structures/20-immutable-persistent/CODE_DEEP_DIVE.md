# Code Deep Dive: Immutable & Persistent Data Structures

Core idea: Persistent structures never mutate: each 'update' returns a new version sharing most nodes with the old (path copying), giving cheap snapshots and time travel.

## Class overview

Single class under `src/` exposing the contract table from THEORY; every public method restores all invariants before returning.

## Key fields

```java
// invariant: no reachable node is ever mutated after publication
// (see THEORY for the full invariant list)
private int size; // maintained on every path, incl. delete
```

- no reachable node is ever mutated after publication
- old roots remain fully readable forever
- sharing is invisible (observe immutability)
- version DAG only grows (GC reclaims unreachable)

## Reference skeleton (fill in the bodies)

```java
public final class LabStructure {
    public LabStructure(/* capacity / params */) { /* empty-state invariant */ }
    public void op0(/* args */) { /* conj(coll,x) [O(log n) nodes] */ }
    public void op1(/* args */) { /* assoc(map,k,v) [O(log n) nodes] */ }
    public void checkInvariants() { /* throw AssertionError on violation */ }
    @Override public String toString() { /* ASCII dump for traces */ return ""; }
}
```

## Hot path: `conj(coll,x)`

```java
// conj(coll,x): new version with x added [O(log n) nodes]
public void hotPath(/* args */) {
    // 1. handle empty / singleton fast paths
    // 2. walk the structure touching O(bound) nodes
    // 3. restore bookkeeping (counts / tags / parents)
    // 4. assert checkInvariants() in debug builds
}
```

Trace it: run two multi-step scenarios by hand and assert the ASCII dump matches.

## Second op: `assoc(map,k,v)`

```java
// assoc(map,k,v): new version with k->v [O(log n) nodes]
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

- `conj(coll,x)`: O(log n) nodes - new version with x added
- `assoc(map,k,v)`: O(log n) nodes - new version with k->v
- `snapshot()`: O(1) - keep a root reference (free)
- `getVersion(v)`: O(log n) - read any historical root
- `diff(v1,v2)`: O(d log n) - walk divergent paths only
- `transientBuild()`: O(n) total - batch via mutable builder then freeze

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
