# Atomic Classes — Theoretical Foundation

## Core Concept

`java.util.concurrent.atomic` provides lock-free read-modify-write on single
variables: `getAndIncrement`, `compareAndSet`, `getAndUpdate` — each a single
hardware CAS (`lock cmpxchg` on x86) with volatile memory effects. No monitor,
no park, no BLOCKED state: a failed CAS just retries the loop.

Implementation note (JDK 23 source): `AtomicInteger` holds `private volatile
int value` plus a `private static final long VALUE` field offset, and
`incrementAndGet()` is literally `U.getAndAddInt(this, VALUE, 1) + 1` — one
Unsafe intrinsic bound to one instruction. The *specification* of the memory
effects is written in terms of `VarHandle` (`compareAndSet`,
`getAndAdd`, ...); the *mechanism* is Unsafe intrinsics underneath.

## The CAS Loop Pattern

Every read-modify-write that isn't a single intrinsic is a loop:

```java
int prev, next;
do {
    prev = atomic.get();            // volatile read
    next = transform(prev);
} while (!atomic.compareAndSet(prev, next));   // single CAS: commit or retry
```

Correctness argument: `compareAndSet` succeeds only if the value is still
`prev` — i.e., nobody modified it since our read. Linearization point = the
winning CAS. Cost model: uncontended ≈ one CAS (~10–20ns x86); contended =
retries burn CPU with no progress guarantee per thread (lock-free:
*some* thread always progresses; *your* thread may starve — same caveat as
lab 08's queue).

`getAndUpdate`/`accumulateAndGet` are this loop pre-written (with the
function applied *outside* the CAS — so side-effecting functions may run
multiple times; the function must be side-effect-free).

## compareAndSet vs compareAndExchange vs weakCompareAndSet

- `compareAndSet(e, x)` → boolean: did I win? (May fail spuriously on some
  platforms — but on x86 it doesn't; the "weak" distinction matters for ARM.)
- `compareAndExchange(e, x)` → the *witness* value (actual current value):
  lets you skip a re-read on failure (`prev = witness; retry`).
- `weakCompareAndSet` → boolean, allowed to fail spuriously even when `e`
  matches: use *only* in retry loops (where spurious failure just costs one
  more iteration), never as a one-shot test. Plain `compareAndSet` is the
  default; weak is the experts' micro-optimization.

## The ABA Problem

CAS checks *value equality*, not *unchanged-since*: value A → B → A reads as
"no change" to `compareAndSet(A, C)`. Consequences bite when the *transitions*
matter (reused nodes in lock-free stacks/queues — pop A, pop B, push A back:
a CAS expecting A succeeds on a different A with a different `next`).

Fixes, in escalating cost order:

1. **Don't reuse identities** (GC-allocated nodes — the CLQ trick from lab
   08: fresh object per offer means A→B→A on the *reference* can't alias).
2. **`AtomicStampedReference<V>`** — (reference, int stamp) pair CASed
   together; stamp increments per mutation so A₁ ≠ A₂.
3. **`AtomicMarkableReference<V>`** — (reference, boolean) pair; cheaper
   one-bit version for deleted-or-not marking.

Stamped references cost a `Pair` allocation per access — use only where ABA
is a real hazard (Treiber stacks, hazard-pointer schemes), not counters.

## Striped Counters: LongAdder / LongAccumulator / DoubleAdder

One CAS word shared by many writers = contention collapse (lab 01 of
collections-deep showed the CHM version: `CounterCell[]`). `LongAdder`
applies the same striping to counters:

- Writers hash to per-thread cells (`Cell[]`, created on demand, grow on
  contention); `sum()` adds `base + Σ cells`.
- `sum()` is **not atomic** — concurrent increments during the sum may be
  missed or double-counted; the result is "at some point during the call"
  fuzzy. `sumThenReset()` exists for quiescent-point metrics.
- Ordering: `LongAdder` beats `AtomicLong` above ~2–4 contending writers;
  below that the cell infrastructure is pure overhead. `DoubleAdder`/
  `DoubleAccumulator` extend to floating point (bit-wise CAS on the long
  representation); `LongAccumulator` generalizes with a binary operator
  (max/min tracking).

## AtomicInteger vs synchronized: The Decision Rule

| | `Atomic*` | `synchronized` |
|---|---|---|
| Single-variable RMW | one CAS, no block | monitor enter/exit, may park |
| Compound multi-variable invariants | impossible (torn across two CASes) | natural (one critical section) |
| Contended throughput | degrades via retries (CPU burn) | degrades via parking (context switches) |
| Memory footprint | object header + value (+ padding) | none extra |
| Semantics on failure | caller retries / moves on | caller waits |

Two atomics can't transact together — `atomicA.set(..); atomicB.set(..)` has
an observable intermediate state. Invariants spanning variables need a lock
(or a single packed `AtomicLong` updated by one CAS, the bit-field trick).

## False Sharing and @Contended

CAS words on the same cache line ping-pong between cores: two unrelated
`AtomicLong`s adjacent in memory contend on *hardware* despite logical
independence. `LongAdder` cells are padded (`@jdk.internal.vm.annotation.
Contended`, 128 bytes with `-XX:-RestrictContended` needed for user code)
precisely to isolate them. Measure first (`-XX:+PrintFieldLayout`, perf
counters), pad second — 128 bytes per counter is real memory.

## Key Invariants

1. Every RMW linearizes at exactly one winning CAS; losers retry with fresh
   reads.
2. Update functions passed to `getAndUpdate`/`accumulateAndGet` must be
   side-effect-free (re-execution is normal, not exceptional).
3. `sum()` on striped counters is a fuzzy snapshot, never an atomic total.
4. ABA safety comes from identity freshness, stamps, or marks — never from
   CAS alone.
5. `@Contended` padding trades memory for contention isolation; default cell
   padding already handles the common case.
