# Inbox Service and Snapshot Readers on List Backends

Inbox. A job inbox serves producers appending tasks and workers taking
them FIFO, with 50 reader threads scanning snapshots. ArrayDeque carries
the queue; CopyOnWriteArrayList carries the snapshots; LinkedHashMap
backs a small LRU over hot jobs. Each backend chosen for its access
shape, with the queue/oracle proof to back it.

Queue lane. 200k enqueue/dequeue script vs LinkedList oracle - order
must match exactly. ArrayDeque vs LinkedList timing at three sizes
quoted; the deque should win locality, shown not claimed.

Snapshot lane. Writer publishes inbox snapshots; readers iterate without
locks. 50-reader soak asserts no ConcurrentModification-style failure
and snapshot freshness within one publish interval. Copy cost per
publish quoted vs inbox size.

LRU lane. LinkedHashMap access-order cache over hot job metadata, cap
1k, hit rate on the replayed access trace quoted with the number.

Surgery lane. LinkedList block moves (O(1) splice given handles) vs
ArrayList shifting at 50k elements - timed pair proving the crossover
where pointer surgery beats memmove.

Edge file. Dequeue on empty (typed signal), snapshot during concurrent
publish (reader sees old-or-new, never torn), LRU eviction order audit,
splice with stale handle (loud failure).

Deliver. Inbox, soak logs, backend comparison table, edge tests. Marks:
oracle parity 12, soak plus snapshot proof 10, backend numbers 8.
## Inbox extras
- 200k script in CI.
- Soak reader count fixed at 50.
- Snapshot cost curve plotted.
- Trace replay hit rate posted.
- Splice crossover noted.
- Empty-dequeue signal tested.
- Eviction order audited.
- Handle-guard test kept.
