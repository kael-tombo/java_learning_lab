# Flashcards — Parallel Algorithms

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Work T₁ | total operations on one processor |
| 2 | Span T∞ | longest dependency chain |
| 3 | Parallelism | T₁/T∞ |
| 4 | Brent bound | T_p ≤ T₁/p + T∞ |
| 5 | Lower bounds | T_p ≥ max(T₁/p, T∞) |
| 6 | Scan span | Θ(log n) |
| 7 | Scan work | Θ(n) |
| 8 | Up-sweep/down-sweep | the two Θ(log n)-span phases of scan |
| 9 | Amdahl speedup | 1/(f + (1-f)/p) |
| 10 | Amdahl ceiling | 1/f as p→∞ |
| 11 | Race condition | unsynchronized access, ≥1 write |
| 12 | Race fixes | atomic, lock, or reduction |
| 13 | Reduction | thread-local partials combined at the end |
| 14 | Fork/join | split, recurse, combine |
| 15 | Fork/join in Java | ForkJoinPool + RecursiveTask/RecursiveAction |
| 16 | Parallel streams | thin layer over ForkJoinPool |
| 17 | Naive parallel merge sort span | Θ(n) (the merge) |
| 18 | Work-efficient merge span | Θ(log² n) via binary-search merge |
| 19 | Critical path | the span — longest dependency chain |
| 20 | Over-splitting | tasks smaller than overhead |
| 21 | Blocking I/O on a worker | stalls that worker — use virtual threads/executor |
| 22 | Parallelism = available concurrency | average number of ready nodes |
| 23 | Amdahl f | serial fraction of the work |
| 24 | Gustafson | weak scaling: larger problems on more processors |
| 25 | Brent on a balanced reduce | T_p ≈ n/p + log n |
| 26 | T₁/T∞ for the sum tree | n/log n |
| 27 | Span of doubling scan | Θ(log n) |
| 28 | Associative operator requirement for parallel scan | the combine must be associative |
| 29 | Min-index scan | works because (min, first-index) is associative |
| 30 | Lock granularity | coarse = slow, fine = complex; prefer lock-free or reduction |
| 31 | AtomicInteger | single-word read-modify-write, race-free |
| 32 | Determinism and races | races make output scheduling-dependent |
| 33 | Shared counter locked | correct but serial — not parallel |
| 34 | Work conservation | T_p ≥ T₁/p always |
| 35 | Span is the floor | no schedule beats T∞ |
| 36 | Binary search merge idea | each side partitions the other by binary search |
| 37 | Amdahl on 10% serial | max 10× speedup ever |
| 38 | Weak vs strong scaling | Gustafson vs Amdahl |
| 39 | Span of for-each map | Θ(1) span, Θ(n) work |
| 40 | Span of tree reduce | Θ(log n) |
| 41 | Work of tree reduce | Θ(n) |
| 42 | Ready nodes | nodes with all dependencies satisfied |
| 43 | Greedy scheduler | runs ready nodes whenever processors are free — achieves Brent |
| 44 | Parallelism from the DAG | T₁/T∞ bounds useful processors |
| 45 | Threshold for fork/join | split until tasks are ~µs of work |
| 46 | Atomic vs synchronized | atomic is lock-free for single-word ops |
| 47 | Deterministic parallel reduce | yes if the combine is associative and the tree shape is fixed |
| 48 | Span of sequential for-sum | Θ(n) |
| 49 | Parallel for-sum span | Θ(log n) with a tree combine |
| 50 | Why scan is useful | it parallelises every linear recurrence |
| 51 | Linear recurrences as scans | s[i] = a[i] + last — associative via 2×2 matrices |
| 52 | Scan of a[i]=i | s[i] = i(i+1)/2 |
| 53 | Down-sweep | distributes the partial prefixes top-down |
| 54 | Up-sweep | combines children into parent sums |
| 55 | Brent assumes greedy scheduling | ready work is never left idle |
| 56 | Practical parallel speedup | min(p, T₁/T∞) |
