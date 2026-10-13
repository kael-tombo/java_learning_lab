# References: Memory Barriers

## Normative sources

- JLS 17.4 (Memory Model): hb rules, DRF guarantee (17.4.3-17.4.5),
  causality (17.4.8) — the verdicts every snippet asserts.
- JLS 17.5 and 17.7 (final fields; non-atomic treatment): the adjacent
  edges (freeze) and the tearing rules that place opaque above plain —
  full treatment in lab 04.
- Doug Lea, *JSR-133 Cookbook for Compiler Writers* (2004): the
  LoadLoad/LoadStore/StoreStore/StoreLoad taxonomy, acquire/release/SC
  assembly, and roach-motel movement — the primary source for this
  lab's THEORY and ARCHITECTURE.
- JSR-133 / Manson-Pugh-Adve, "The Java Memory Model" (POPL 2005):
  the specification behind the cookbook's lowering targets.

## Books and guides

- Brian Goetz et al., *Java Concurrency in Practice* (2006): chapter
  16 (JMM) and chapter 3 (visibility/publication) — the practitioner
  companion; safe-publication patterns priced by this lab's ladder.
- Nitsan Wakart, "The volatile read/write cost" and related
  mechanical-sympathy notes: independent x86 measurements in the same
  ladder shape (plain ~1 ns, fenced stores an order up, reads cheap).
- Jeff Preshing, "Acquire and Release Semantics" / "Memory Ordering at
  Compile Time": cookbook-equivalent treatment with C++ litmus that
  maps directly onto VarHandle modes.

## OpenJDK sources (JDK 9+ layout, stable paths)

- `src/java.base/share/classes/java/lang/invoke/VarHandle.java`:
  `getOpaque`/`setOpaque`/`getAcquire`/`setRelease`/volatile
  specifications — the mode lattice used in snippets 3 and 5.
- `src/java.base/share/classes/java/util/concurrent/atomic/AtomicIntegerArray.java`:
  `set` (volatile) vs `lazySet` (release) — snippet 1-3's comparison
  surface.
- `src/java.base/share/classes/java/util/concurrent/locks/StampedLock.java`:
  documented optimistic/acquire-Fence validation — JDK-internal fence
  application of the same taxonomy.
- `src/java.base/share/classes/java/util/concurrent/ConcurrentHashMap.java`
  (table volatiles) and `.../locks/AbstractQueuedSynchronizer.java`
  (state volatiles/CAS): production release/acquire chains of the lab
  02 snippet-4 shape, at scale.

## Testing and tooling

- OpenJDK jcstress (`github.com/openjdk/jcstress`): verdict
  histograms for snippets 4-5 shapes; the correct promotion path for
  hand-rolled 2000/20000-round drivers.
- `-XX:+PrintAssembly` with hsdis: visual confirmation of the ladder's
  big step (locked op on the volatile-store path, bare MOVs elsewhere).
