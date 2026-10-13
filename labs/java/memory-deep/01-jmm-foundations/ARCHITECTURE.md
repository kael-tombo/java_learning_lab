# Architecture: Where the JMM Sits in the Stack

## The five-layer picture

```
Java source (your code: locks, volatiles, starts, joins, latches)
  v  javac (bytecode; preserves synchronization actions as such)
JIT compilers C1/C2 (reorder freely EXCEPT across hb actions)
  v  hardware (out-of-order issue, store buffers, invalidate queues)
Cache coherence MESI (eventual delivery; ordering NOT guaranteed)
  ==> observed behavior, constrained ONLY by happens-before edges
```

The JMM is the contract between the top layer and everything below:
the implementation may do anything invisible, and must honor every hb
edge. There is no other constraint. That asymmetry is the whole design.

## What each layer may and may not move

- **javac**: mostly faithful; emits `monitorenter/exit`,
  `getfield/putfield` with volatile flags, `invoke Thread.start`.
  It does not reorder across synchronization actions.
- **C1/C2 JIT**: aggressive within a thread (inlining, hoisting,
  elimination) under as-if-serial semantics; pinned at synchronization
  actions. A volatile access or monitor op is a compiler barrier: the
  JIT will not hoist a load above an acquire or sink a store below a
  release, and it emits the CPU fence the platform needs.
- **CPU**: executes out of order around stalls, buffers stores in a
  per-core FIFO, forwards a core's own pending store to its own loads.
  Single-threaded code never notices (commit stays in order); other
  cores notice constantly unless fences drain the buffers.
- **Coherence (MESI)**: guarantees every write eventually reaches every
  core and that a single location has a total write order. It does NOT
  order *different* locations relative to each other. Cross-location
  order comes only from program fences derived from hb edges.

## Where each hb edge becomes a fence

- `start()`: the spawning thread's prior writes are flushed to a point
  the new thread must observe; the JIT emits a release before the
  native thread creation and the child begins with an acquire.
- `join()`: symmetric — the worker's writes are released at exit and
  the joiner acquires on successful join return.
- Monitor `unlock -> lock`: unlock emits a release (prior critical
  section stores drain before the lock word releases); lock emits an
  acquire (later reads cannot move above it). The lock word itself is
  the rendezvous point both sides agree on.
- Volatile write -> volatile read: release store plus acquire load,
  with sequential-consistency fencing after the store on platforms that
  need it (lab 03 measures the x86 price: the store fence).
- `CountDownLatch`: implemented on AQS volatiles internally, so
  `countDown()` chains a volatile write to the `await()` volatile read
  path — a library edge with the same release/acquire skeleton, no user
  fences required.

## Why this layering matters for the demos

- `StartEdge` (checksum 1499500) works because the start edge crosses
  all four lower layers at once: nothing below may hide the 1000
  element writes from the child.
- `LockEdge` (2M exact increments) works because every unlock/lock pair
  re-rendezvouses the two sides through the same lock word; the chain
  of 2M edges is one total order regardless of core count.
- `CausalityFloor` shows the layer below the contract: with no edge at
  all, coherence still delivers only real written values (0..100000),
  in arbitrary staleness and order. Coherence gives *values*;
  happens-before gives *order*. The lab separates the two deliberately.

## Design consequences

- Order is opt-in per relationship, not global: you pay (in fences)
  exactly for the edges you declare, nowhere else.
- Library edges reuse the same skeleton: queues, futures, executors
  all reduce to volatile/cas chains inside `java.util.concurrent`.
- Portability is structural: the same hb edge compiles to `XCHG` on
  x86, `STLR/LDAPR` plus fences on ARM64 — your source does not change.
