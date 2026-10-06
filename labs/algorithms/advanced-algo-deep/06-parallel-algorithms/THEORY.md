# Theory — Parallel Algorithms

Parallel analysis replaces the single running-time number with two numbers: how much total work there is, and how long the longest dependency chain is. Everything else — Brent, Amdahl, race conditions — follows from treating computation as a DAG of work and dependencies.

## Work, span, and the DAG model

A computation is a DAG: nodes are unit-time instructions, edges are data/control dependencies. **Work T₁** is the number of nodes — the time on one processor. **Span T∞** is the length of the longest path — the time on infinitely many processors, because that path is inherently sequential. **Parallelism** T₁/T∞ is the average available concurrency. A schedule on p processors cannot beat either bound: T_p ≥ max(T₁/p, T∞). Brent's theorem says you can get close: greedy scheduling achieves T_p ≤ T₁/p + T∞.

## Brent's theorem, stated carefully

At each step, every ready node is either being executed or is waiting. At most p ready nodes can execute; each such step still reduces the critical path, so the number of "waiting" steps is at most T∞. Hence `T_p ≤ T₁/p + T∞`. With enough processors (p ≈ T₁/T∞), `T_p = Θ(T∞)` — the span is the floor.

## Parallel prefix sum (scan)

Scan computes s[i] = a[0]+…+a[i]. The sequential version is Θ(n) work and Θ(n) span. A parallel scan runs in two Θ(log n) span phases: an up-sweep (reduce) that builds partial sums bottom-up, and a down-sweep that distributes prefixes top-down. Work remains Θ(n). Span drops from Θ(n) to Θ(log n) because the tree of partial sums has depth log n. This works for any associative operator, including min-index.

## Merge sort and other divides

Parallel merge sort: split, sort both halves in parallel (span T(n/2)), merge in Θ(n). Span: `S(n) = S(n/2) + Θ(n)` = Θ(n) — the naive merge dominates the span. A binary-search-based merge reduces the merge span to Θ(log² n). The lesson: the *merge* is the long pole.

## Amdahl's law

If a fraction f of the work is sequential, the best speedup on p processors is `1/(f + (1-f)/p)`, which tends to `1/f` as p → ∞. Doubling cores forever never beats the sequential fraction.

## Race conditions

A race is two unsynchronised accesses to the same location where at least one is a write. It makes the result depend on scheduling. Fixes: an atomic for counters, a lock for multi-word invariants, or a *reduction* for accumulations — the preferred fix because it removes the shared write entirely.

## Fork/join and the Java model

Fork/join splits a task into subtasks, runs them, and joins their results — a structural match to the DAG model. In Java, `ForkJoinPool` + `RecursiveTask`/`RecursiveAction` implement it; parallel streams are a thin layer. Pitfalls: un-forkable tasks (blocking I/O), over-splitting (task overhead exceeds the work), and shared mutable state (races).

## Choosing a model

| Workload | Tool | Why |
|----------|------|-----|
| Divide-and-conquer | fork/join | structural match to the DAG |
| Array map/reduce | parallel streams | no dependencies |
| Associative combine | scan/reduction | Θ(log n) span possible |
| Heavy blocking I/O | virtual threads/executor | workers must not block |
| Irregular graph | explicit task queue | poor fork/join fit |

## Pitfalls

- Treating speedup as linear in cores — Amdahl and the span bound both cap it.
- Races from shared counters — use an atomic, a lock, or a reduction.
- Measuring wall-clock on one machine and calling it "parallel" — measure work and span.
- Over-splitting into tasks smaller than the fork/join overhead.
