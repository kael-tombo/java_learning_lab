# History: Lock-Free Queues

## Michael and Scott (1996)

**Maged Michael** and **Michael Scott**, "Simple, Fast, and Practical
Non-Blocking and Blocking Concurrent Queue Algorithms" (*PODC 1996*) —
the two-pointer (head/tail) CAS queue with lagging pointers. The JDK
source cites the algorithm directly; CLQ is its production embodiment
with the slack optimization and GC-aware self-linking added.

## Doug Lea and java.util.concurrent (2004)

**Doug Lea** wrote the `java.util.concurrent` package (JSR 166, Java 5,
2004), including `ConcurrentLinkedQueue`. Key adaptations from the paper:
slack threshold of 2 (fewer volatile writes), self-linked dequeued nodes
for garbage retention behavior the paper's memory-managed setting never
faced, and weakly consistent iterators instead of the paper's bare API.

## VarHandle modernization (Java 9+)

JDK 9 replaced `sun.misc.Unsafe` CAS calls with `VarHandle`
(`ITEM`, `NEXT` handles) — same semantics, standard API. Behavior and
linearization points unchanged since 1.5; only the CAS spelling moved.

## Siblings in the same package

- `LinkedBlockingQueue` (optionally bounded, two locks + conditions,
  blocking `take`) — when you need backpressure or waiting.
- `ArrayBlockingQueue` (bounded array + one lock) and `SynchronousQueue`
  (rendezvous) cover the bounded/hand-off corners CLQ deliberately skips.
