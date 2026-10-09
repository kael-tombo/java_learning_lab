# Architecture: Set Abstractions in Code

## The Collection Hierarchy (Java)

```
Iterable
 └── Collection
      ├── List        (ordered, duplicates allowed)
      ├── Set         (no duplicates)
      │    ├── HashSet        (hash table, O(1) avg)
      │    │    └── LinkedHashSet (insertion order)
      │    ├── TreeSet        (red-black tree, sorted, O(log n))
      │    └── Set.of(...)    (immutable, Java 9+)
      └── Queue/Deque
```

`Set` is a *contract*, not an implementation: at most one element equal to any given object, `add` returns false on duplicates, and iteration visits each element once. Everything else (ordering, null policy, thread safety) is decided by the concrete class — so choose the class by required iteration order and universe size, not by the word "set."

## Layers of a Set-Based Module

1. **Domain layer** — value types with structural equality (`record`, or `equals`/`hashCode` written together). This is where "what counts as the same element" is defined; the whole architecture rests on it.
2. **Operation layer** — pure functions `union`, `intersect`, `difference`, `complement`, `powerSet`, written against the `Set` interface so the backing structure can change.
3. **Storage layer** — `HashSet` for point queries, `TreeSet` for ordered/range queries, `BitSet` when the universe is a contiguous integer range.
4. **Boundary layer** — convert inputs once (arrays/streams → Set), run algebra, convert out. Keeping conversions at the boundary avoids repeated O(n) materializations in the core.

## Why Interfaces Are the Architecture

A method declared `Set<String> resolve(Set<String> allowed, Set<String> requested)` documents intent as algebra: the caller expects something like `requested ∩ allowed`. Declaring `List<String>` instead would allow duplicates and order dependence, silently changing semantics. The type is the specification.

## Bitset vs Hashset: An Architectural Fork

- Universe known, dense, ≤ ~10⁶ → `BitSet`. Cost: operations are Θ(n/64) words; complement needs an explicit `universeSize` argument (a BitSet has no intrinsic universe — it extends to infinity with zeros).
- Universe open-ended or sparse → `HashSet`. Cost: hashing and allocation per element.
- Mixed universe (ints but sparse) → `HashSet<Integer>` with boxing overhead, or a hybrid: dense `BitSet` for small ids plus a `HashSet` for large ones.

Document which side you chose in the class Javadoc — the choice changes both complexity and memory by orders of magnitude.

## Set Algebra in Specs and Tests

A useful test architecture: generate a small random universe (say 8 elements), derive random A and B as bit vectors, and assert identities (De Morgan, distributivity, absorption) against both the `Set` implementation and the bitwise reference. Because characteristic vectors make each operation O(1) per element, the bitwise model is a trustworthy oracle for the hash/tree implementation.

## Threading Model

No `java.util.Set` is thread-safe for concurrent mutation. Options: (a) wrap with `Collections.synchronizedSet` (all ops O(1) overhead plus lock), (b) `CopyOnWriteArraySet` for read-mostly, tiny sets (each write copies O(n)), or (c) confine the set to one thread. Unbounded concurrent `add` is also a memory-growth attack surface; bound the set's size at the boundary.
