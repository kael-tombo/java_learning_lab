# Internals: How OpenJDK Implements the Edges

## Compiler barriers first, CPU fences second

Every hb edge does two jobs: it constrains the JIT (do not move memory
operations across this action) and it emits whatever CPU fence the
platform requires (possibly none). On x86 many edges are compiler-only
(an acquire load is a plain MOV with a compiler barrier); the volatile
store additionally needs a fenced instruction. On ARM64 the same edges
lower to LDAPR/STLR plus DMB where sequential consistency demands it.
The JMM rule is platform-independent; the fence selection is not.

## Where the implementation lives (OpenJDK, qualitatively)

- **Interpreter and C1/C2**: volatile accesses and monitor operations
  are distinct IR nodes from plain accesses, so optimization passes
  (loop hoisting, commoning, sinking) treat them as pins they cannot
  move memory operations across. Removing the `volatile` keyword lowers
  the node to a plain access — which is exactly why deleting one word
  reopens hoisting bugs.
- **Thread lifecycle**: `Thread.start()` crosses into native thread
  creation with release semantics on the spawner side; the new thread
  begins with acquire semantics. `join()` (via park/unpark and alive
  checks in `java.lang.Thread` plus hotspot thread-state machinery)
  acquires on successful return.
- **Monitors**: objectMonitor enter/exit paths pair an acquire on entry
  with a release on exit around the critical section; biased/thin/thick
  locking variants differ in mechanics, not in the hb contract.
- **java.util.concurrent**: `CountDownLatch`, queues, and futures build
  on internal volatiles and CAS (AbstractQueuedSynchronizer state).
  The documented `countDown()` hb `await()` edge is realized as ordinary
  volatile chains inside the JDK — no magic, just specified layering.

## Cache coherence vs ordering, concretely

MESI-style coherence gives two properties and pointedly not a third:
(1) every write eventually becomes visible everywhere; (2) all cores
agree on a single order of writes to *one* location. It never orders
writes to *different* locations — that is what fences add. So
`StartEdge`'s 1000 writes arrive via coherence, but only the start edge
tells the child *when* the set is complete; without it the child could
observe any prefix at any time.

## Why the demo values are exact, mechanically

- 1499500: the start edge forces the child's 1000 loads after all 1000
  stores in coherence order completion — a full array, not a prefix.
- 41541750: the join edge forces the main thread's 500 loads after all
  worker stores — every square present.
- 2000000: the monitor chain serializes 2M read-modify-write bodies so
  each sees its predecessor — zero lost updates by construction.
- Latch `true`: the countDown/await volatile chain plays the same role
  as start/join for a thread pair the spawner does not own.

## What the JIT must never do at an edge

Hoist a load above an acquire. Sink a store below a release. Eliminate
a synchronization action it deems redundant without proving no other
thread observes it. Merge two volatile accesses to one location. Each
prohibition is the compiler side of one hb rule; `-XX:+PrintCompilation`
surprises virtually always trace to one of these four being (wrongly,
in broken code) assumed absent.
