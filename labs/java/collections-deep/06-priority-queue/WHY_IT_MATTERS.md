# Why PriorityQueue Matters

## Where it shows up

- **Dijkstra / A***: the frontier is a min-heap keyed by distance. Every
  relaxation is an `offer`; every settled node is a `poll`. Stale entries
  (a node re-offered with a shorter distance) are skipped on poll by
  comparing against settled distances — the standard lazy-deletion idiom.
- **K-way merge**: merging k sorted runs (external sort, LSM-tree reads)
  holds one head element per run in the heap — O(n log k) total instead of
  O(n·k) scanning.
- **Top-k / streaming**: `stream.sorted().limit(k)` uses a bounded heap
  internally; hand-rolled variants keep a max-heap of size k
  (`Comparator.reverseOrder()`).
- **Event simulation / schedulers**: next-event-first processing; timers in
  `ScheduledThreadPoolExecutor` use a `DelayedWorkQueue` (a heap variant).

## What goes wrong without it

Teams reach for `Collections.sort` in a loop (O(n log n) per extraction),
or `TreeSet` with a comparator that returns 0 for distinct tasks — silently
dropping work because Set semantics deduplicate. PriorityQueue's
duplicates-retained behavior is the safer default for scheduling.

## Interview signal

Expect: "why is iteration unsorted?", "offer vs add?", "heapify cost?",
"how would you get top-k?". The answers are all one invariant deep: the
array is a heap, only the root has a contract, bulk build is O(n).
## When not to reach for it

- Membership-heavy logic (`contains` per tick) — O(n) scans; pair with a
  `HashSet` or pick a different structure.
- Multi-threaded producers/consumers — silent corruption; the blocking
  sibling or external confinement is mandatory, not optional.
- Small fixed n with exact sorted output each tick — a sorted array or
  `TreeSet` with total-order comparator can be simpler and iteration-clean.

The rule: PriorityQueue wins when min-extraction dominates and threads and
membership don't. Outside that triangle, its sharp edges (heap-order
iteration, O(n) scans, no locks) cut.
