# Performance: PriorityQueue

| Operation | Cost | Why |
|---|---|---|
| offer / add | O(log n) | one siftUp path |
| poll | O(log n) | last-to-root + siftDown |
| peek | O(1) | `queue[0]` |
| contains / remove(Object) | O(n) + O(log n) | `equals` scan, then sift |
| iterator step | O(1) amortized | raw index walk |
| addAll(Collection) | O(n) | heapify, not n offers |
| poll-all drain | O(n log n) | n × siftDown |

## Constants that matter

- Zero allocation on offer/poll (element moves within the array). Only
  growth allocates — and growth copies references (`arraycopy`-style),
  not elements.
- Cache behavior: children of k are 2k+1, 2k+2 — adjacent slots, usually
  one cache line for small k. Sift paths walk contiguous-ish memory,
  unlike pointer-chasing heaps.
- Measured growth: 11 → 24 → 50 → 102 → 153 → 229 → 343. Bulk-load with
  `new PriorityQueue<>(collection)` to skip the early doubling steps.

## Scaling guidance

- n = 10⁶: offer/poll ≈ 20 comparisons each — sub-microsecond with a cheap
  comparator. A comparator that allocates or calls `compareTo` on boxed
  BigDecimals can dominate; keep it branch-light.
- `contains` on a 1M heap scans 1M slots — pair with a `HashSet` if you
  need membership + priority (add/remove in both).
- PriorityQueue is unsynchronized: single-threaded throughput is the best
  case. Under contention, `PriorityBlockingQueue` serializes on one lock —
  expect writer throughput to flatten at ~1/lock-hold-time.
