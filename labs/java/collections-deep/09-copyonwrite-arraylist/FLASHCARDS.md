# Flashcards: CopyOnWriteArrayList

**Q: Shared state field?**
A: `volatile Object[] array` — the whole protocol.

**Q: Read path?**
A: `elementAt(getArray(), i)` — volatile read + load, no lock, O(1).

**Q: Write path?**
A: synchronized(lock) → copy → mutate copy → setArray publish. O(n).

**Q: Iterator semantics?**
A: Pins array at construction; exact snapshot; never CME.

**Q: Iterator mutation?**
A: remove/set/add → UnsupportedOperationException.

**Q: set() with equal value?**
A: Still copies + setArray — volatile-write heartbeat.

**Q: addIfAbsent fast path?**
A: Lock-free scan hit → return false, no lock taken.

**Q: remove fast path?**
A: Lock-free scan miss → return false, no lock taken.

**Q: Lost-race handling?**
A: Under lock, re-scan prefix if snapshot != current.

**Q: Nulls?**
A: Allowed — unlike concurrent queues.

**Q: equals?**
A: AbstractList element-wise — equals an ArrayList with same elements.

**Q: Ideal workload?**
A: Reads >> writes (100:1+), small n: listeners, config, routes.

**Q: Iterator retention?**
A: Each pins one array version — scope tightly.
