# Performance: CopyOnWriteArrayList

| Operation | Cost | Locking |
|---|---|---|
| get(i) | O(1) | none — volatile read |
| add(e) | O(n) copy + alloc | synchronized |
| set(i, e) | O(n) clone + store | synchronized |
| remove(o) | O(n) scan + O(n) copy | only on hit |
| addIfAbsent(e) | O(n) scan; copy only on miss | only on miss |
| iterator() / step | O(1) pin / O(1) walk | none, ever |

## Worked numbers

- n = 1M (8MB of refs): one `add` allocates ~8MB and copies 1M refs
  (~0.5–2ms). 100 adds/sec = 800MB/sec garbage — young-gen churn dominates
  the profile, not the copy loop.
- n = 100 listeners, 10k reads/sec, 1 write/min: reads cost ~nothing
  extra; writes cost 100-ref copies. Ideal COW shape.
- `CopyOnWriteArraySet` (`addIfAbsent` adds): every add scans O(n) first —
  set semantics at list prices; fine for tens of elements, hopeless past
  thousands.

## Scaling guidance

- Readers scale linearly with cores (no shared mutable state — only the
  volatile read, which doesn't bounce until a write publishes).
- Writers serialize on `lock` AND each pays O(n): write throughput ≈
  1/copy-time regardless of core count. Two writers don't parallelize.
- Memory: each iterator pins one array version; bursty writes + slow
  iteration = multiple full arrays live. Bound iterator lifetimes or copy
  to a plain list first for long processing.
