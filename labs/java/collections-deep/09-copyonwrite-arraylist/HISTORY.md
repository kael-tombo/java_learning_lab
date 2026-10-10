# History: Copy-on-Write in Java

## The technique

Copy-on-write predates Java: VM kernels (e.g. Mach, BSD `fork`) shared
pages read-only until a write fault copied them. Applying COW to
user-level collections traded memory churn for lock-free reads — the same
bargain at a different layer.

## Doug Lea and JSR 166 (2004)

`CopyOnWriteArrayList` and `CopyOnWriteArraySet` shipped in **Java 5
(2004)** as part of **Doug Lea**'s `java.util.concurrent` package
(JSR 166). The design answered the listener-list problem: event sources
(beans, Swing models, network dispatchers) notify many threads far more
often than listeners register/unregister — and iteration during
notification must never throw CME.

## Design lineage

- `Vector`/`synchronizedList` (Java 1.0–1.2): in-place mutation under a
  lock; iteration fails fast — CME during notify loops was the chronic
  pain COW eliminates.
- Persistent/functional lists (Okasaki, *Purely Functional Data
  Structures*, 1998) share the version-chain insight; COW is its pragmatic
  mutable cousin (O(n) copy instead of O(log n) path-copy, but O(1)
  indexed reads).
- The equal-value `setArray` heartbeat and optimistic
  `addIfAbsent`/`remove` revalidation are JDK refinements added as the
  memory-model implications (JLS §17.4, Java 5 memory-model revision by
  **Jeremy Manson**, **Brian Goetz**, Doug Lea) were worked through.
