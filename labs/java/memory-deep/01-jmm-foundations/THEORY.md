# JMM Foundations — Theoretical Foundation

## Core Concept

The Java Memory Model (JMM — JLS §17.4, rewritten by JSR-133 for Java 5)
answers one question: **which writes can a read observe?** Without
synchronization, the answer is "any of them, or none, in any order" —
compilers, CPUs, and caches all reorder freely. The JMM draws the lines
that civilize this chaos: program order, synchronization actions, and the
*happens-before* partial order built from them.

## The Foundational Guarantee: DRF ⇒ Sequential Consistency

The JMM's central promise (JLS §17.4.3–17.4.5):

> A program is *correctly synchronized* iff every sequentially consistent
> execution is data-race-free. And: **correctly synchronized programs
> exhibit only sequentially consistent behaviors.**

In plain terms: if you eliminate data races (every shared access ordered by
happens-before edges), your program behaves *as if* threads interleaved
one atomic action at a time — the intuitive model. Concurrency reasoning
then reduces to interleaving reasoning. Race freedom buys back simplicity;
that trade is the entire economic basis of locks, volatiles, and
concurrent libraries.

## Happens-Before: The Relation (JLS §17.4.5)

`hb(a, b)` — a happens-before b — is the transitive closure of:

1. **Program order**: within a thread, earlier actions hb later ones
   (as-observed-by-that-thread; the implementation may reorder invisibly).
2. **Monitor rule**: unlock(M) hb every later lock(M).
3. **Volatile rule**: write(V) hb every later read(V).
4. **Thread rules**: `start()` hb the thread's first action; the thread's
   last action hb `join()`'s return; interruption and `isAlive`/`join`
   have specified edges.
5. **Final fields**: freeze at constructor end hb every read that sees the
   reference (lab 04's topic).
6. **Library rules**: `java.util.concurrent` documents one per primitive —
   `countDown()` hb `await()` return, `submit()` hb task execution,
   `put()` hb `take()` receipt, and so on.

A *data race* is two conflicting accesses (same variable, ≥1 write) **not**
ordered by hb. Races forfeit sequential consistency — and with it, every
intuition (this lab's snippets 1–4 show the *ordered* side; the chaos side
needs no demo, only avoidance).

## Sequential Consistency, Precisely

An execution is sequentially consistent if there is a *total order* over
all actions consistent with each thread's program order, and each read sees
the most recent write in that order. It is the "take turns instantly"
model. The DRF guarantee says: no races ⟹ some SC execution explains what
you observed. Debugging then means enumerating interleavings, not hardware
states — the only concurrency mental model that scales to human brains.

## Causality: No Out-of-Thin-Air (JLS §17.4.8)

The JMM additionally requires *causality*: values must have a causal chain
from writes. The famous forbidden outcome:

```java
// initially x = y = 0
// Thread 1: r1 = x; y = r1;
// Thread 2: r2 = y; x = r2;
// FORBIDDEN: r1 == r2 == 42
```

No write of 42 exists anywhere, so 42 cannot be read — even though a naive
"any reordering" story could justify it (compiler speculating the writes
early). Causality bans speculation that invents values. Practical edge:
this is why `Unsafe` publication and clever racy idioms can't produce
*impossible* values — only *stale or reordered* real ones. The values you
see always came from somewhere; the order is what's unreliable.

## Observable Behavior: What "Correct" Even Means

The JMM defines a program's meaning by its *observable* actions
(synchronization actions + external I/O-ish actions: volatile accesses,
locks, thread lifecycle, `System.out` transitively...). Two executions with
identical observable behavior are indistinguishable *by definition* — which
licenses every optimization that preserves them (dead-code elimination,
reordering, hoisting). The as-if-serial rule for single threads and the
hb rules for multi-threaded programs are the same idea at two scopes:
*change anything unobservable; preserve everything observable.*

## JSR-133 in One Paragraph of History

Pre-2004 (original JMM, 1996): volatiles were widely misunderstood
(implementation-dependent semantics), DCL was broken, `final` had no
thread-safety story, and the spec permitted out-of-thin-air reads. JSR-133
(Manson, Pugh, Goetz et al., Java 5/2004) rewrote §17.4 with happens-before,
fixed `volatile`, made DCL correct *with* volatile, gave `final` fields
publication safety, and added the causality requirements. Every rule in
this file dates to that rewrite — 20+ years stable, which is why the
concurrency-deep labs can treat it as bedrock.

## Key Invariants

1. No hb edge between conflicting accesses = data race = no SC guarantee.
2. Race-free programs behave as total-order interleavings (DRF ⇒ SC).
3. Values are never invented (causality); only order/staleness vary.
4. Library primitives extend hb across threads (latch/queue/executor edges).
5. Optimizations preserve observable behavior only — everything else moves.
