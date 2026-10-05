# Code Deep Dive: Spatial Data Structures (R-tree / QuadTree / k-d tree)

Core idea: Spatial indexes partition 2-D/3-D space (grids, quadtrees, R-trees, k-d trees) so range and k-NN queries prune whole regions via bounding boxes.

## Class overview

Single class under `src/` exposing the contract table from THEORY; every public method restores all invariants before returning.

## Key fields

```java
// invariant: every point lies inside its ancestors' MBRs
// (see THEORY for the full invariant list)
private int size; // maintained on every path, incl. delete
```

- every point lies inside its ancestors' MBRs
- siblings may overlap (R-tree) but leaves partition the set
- split keeps fill above m (e.g. 40%)
- mindist(q, MBR) lower-bounds any point inside

## Reference skeleton (fill in the bodies)

```java
public final class LabStructure {
    public LabStructure(/* capacity / params */) { /* empty-state invariant */ }
    public void op0(/* args */) { /* insert(point) [O(log n) avg] */ }
    public void op1(/* args */) { /* rangeQuery(rect) [O(log n + m)] */ }
    public void checkInvariants() { /* throw AssertionError on violation */ }
    @Override public String toString() { /* ASCII dump for traces */ return ""; }
}
```

## Hot path: `insert(point)`

```java
// insert(point): place into leaf, split on overflow [O(log n) avg]
public void hotPath(/* args */) {
    // 1. handle empty / singleton fast paths
    // 2. walk the structure touching O(bound) nodes
    // 3. restore bookkeeping (counts / tags / parents)
    // 4. assert checkInvariants() in debug builds
}
```

Trace it: run two multi-step scenarios by hand and assert the ASCII dump matches.

## Second op: `rangeQuery(rect)`

```java
// rangeQuery(rect): DFS pruning disjoint MBRs [O(log n + m)]
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

- `insert(point)`: O(log n) avg - place into leaf, split on overflow
- `rangeQuery(rect)`: O(log n + m) - DFS pruning disjoint MBRs
- `nearest(q)`: O(log n) avg - best-first with mindist bound
- `kNN(q,k)`: O(k log n) avg - bounded priority queue search
- `bulkLoad(points)`: O(n log n) - STR sort-tile-recursive
- `delete(point)`: O(log n) - remove + condense underfull nodes

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
