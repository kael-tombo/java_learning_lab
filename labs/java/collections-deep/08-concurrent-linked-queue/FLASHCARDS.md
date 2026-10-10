# Flashcards: ConcurrentLinkedQueue

**Q: Algorithm and author?**
A: Michael–Scott lock-free queue (1996); JDK port by Doug Lea (Java 5).

**Q: Node fields?**
A: `volatile E item`, `volatile Node<E> next`. No prev.

**Q: offer linearization?**
A: `NEXT.compareAndSet(p, null, newNode)`.

**Q: poll linearization?**
A: `p.casItem(item, null)` — one winner per node.

**Q: Slack rule?**
A: Head/tail CAS forward only when ≥ 2 steps stale (`p != t` / `p != h`).

**Q: `p == q` means?**
A: Self-linked dequeued node → restart from head.

**Q: Why self-link?**
A: Walker signpost + severs chain for GC.

**Q: size() cost?**
A: O(n) walk, stale on return. isEmpty probes to first live item.

**Q: offer(null)?**
A: NPE — null is the dequeued sentinel.

**Q: Iterator guarantee?**
A: Weakly consistent: never CME, fuzzy under mutation.

**Q: Lock-free meaning?**
A: System always progresses; individuals may starve (not wait-free).

**Q: No blocking ops — alternative?**
A: `LinkedBlockingQueue.take()` (locks + conditions).

**Q: ABA safety?**
A: One-way state transitions + fresh nodes per CAS — no reuse.
