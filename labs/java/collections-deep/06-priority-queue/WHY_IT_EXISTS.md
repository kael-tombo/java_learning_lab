# Why PriorityQueue Exists

Sorted structures answer the wrong question for scheduling. A `TreeSet`
maintains total order at O(log n) per op — but a task scheduler, Dijkstra
frontier, or merge loop only ever needs the *minimum*, repeatedly. Paying
to keep the other n−1 elements ordered is wasted work.

The heap buys exactly the needed contract:

- min available in O(1) (`queue[0]`),
- insert/extract-min in O(log n) with no node allocation,
- bulk build in O(n) via heapify.

Alternatives and why they lose for this job:

- Sorted array: insert O(n) shifts — dead on arrival for interleaved
  insert/remove.
- `TreeSet`: O(log n) too, but per-entry node allocation, comparator-total
  ordering, and no duplicates (Set semantics drop equal-priority tasks
  unless you add tiebreakers).
- Unsorted list + linear min-scan: O(1) insert but O(n) extract — fine for
  tiny n, collapses past a few thousand elements.

PriorityQueue keeps duplicates (heap cares about `compareTo` position, not
`equals` uniqueness), allocates one flat array, and never moves more than
one root-to-leaf path per op. That is the niche: repeated min-extraction
with minimal bookkeeping.
## Why a Queue, and why unbounded

The 2004 Queue framework (`Queue`, `BlockingQueue`, `offer`/`poll`/`peek`
with null-instead-of-throw) separated "waiting" from "ordering": blocking
variants add locks and conditions, PriorityQueue adds ordering, and the
interface stays shared. Unboundedness is the same narrowing — no capacity
argument, no full-queue policy — so `offer` never needs a failure path
beyond NPE. When you need bounds or blocking, the framework points at
`ArrayBlockingQueue` and `PriorityBlockingQueue` instead of complicating
this class.
