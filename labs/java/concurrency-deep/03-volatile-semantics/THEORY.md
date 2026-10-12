# Volatile Semantics — Theoretical Foundation

## Core Concept

`volatile` gives a field two properties and nothing more:

1. **Visibility** — a write to a volatile field *happens-before* every
   subsequent read of that field (JLS §17.4.5). No stale caches, ever.
2. **Atomicity of access** — reads/writes of the volatile itself are atomic,
   *including* `long` and `double` (JLS §17.7 permits tearing for
   non-volatile 64-bit fields; `volatile` forbids it).

What it does **not** give: atomicity of *compound* actions. `volatile int
count; count++` is a race — read, modify, write as three steps with no mutual
exclusion. Visibility ≠ atomicity is the sentence this whole lab hangs on.

## Happens-Before: The Four Rules You Use Daily (JLS §17.4)

1. **Program order**: within one thread, each action happens-before the next
   in program order (as-if — the JVM may reorder invisibly as long as the
   thread itself can't tell).
2. **Volatile**: a write to volatile V happens-before every later read of V.
3. **Monitor**: unlock of M happens-before later lock of M (lab 02's edge).
4. **Thread lifecycle**: `start()` happens-before the thread's first action;
   the thread's last action happens-before `join()` returns; interruption and
   executor-submit/shutdown have their own edges (`java.util.concurrent`
   documents one per action — "actions prior to submitting a Runnable
   happen-before its execution").

Transitivity chains them: write X → write volatile V → read V → read X means
the read of X sees the write. This *piggybacking* pattern (snippet 3) is how
a single volatile flag safely publishes arbitrarily much non-volatile data.

## What the Hardware Does (x86 vs ARM, qualitatively)

The JVM inserts memory barriers to implement the edges; the cost depends on
the CPU's memory model:

- **x86 (TSO — strong model)**: loads are never reordered with loads, stores
  never with stores. A volatile *read* is nearly free (no fence needed —
  just no compiler reordering). A volatile *write* needs a StoreLoad fence
  (HotSpot uses `xchg`, which implies `lock` prefix full barrier) — on the
  order of ~10–20ns, comparable to an uncontended CAS.
- **ARM/POWER (weak model)**: both directions need explicit fences
  (`dmb ish` on ARMv8 for the full-fence cases). Volatile costs more there
  than on x86 — which is why "volatile is cheap" benchmarks don't port.

You never emit barriers yourself (`Unsafe`/`VarHandle` aside); the point is
cost intuition: volatile reads ≈ plain reads on x86, volatile writes ≈
fences everywhere.

## The Double-Checked Locking Story (why JSR-133 exists)

Pre-Java-5 DCL was broken:

```java
// BROKEN without volatile (pre-2004 semantics AND post-2004 without volatile)
Helper helper;
Helper get() {
    if (helper == null) {                    // (1) unsynchronized read
        synchronized (this) {
            if (helper == null)
                helper = new Helper();       // (2) construct + publish
        }
    }
    return helper;
}
```

Without `volatile`, step (2)'s object construction (allocate → init fields →
assign reference) can be *reordered* so the reference publishes before the
fields initialize — a second thread passes check (1), reads a non-null but
half-constructed object. JSR-133 (Java 5, 2004 — the memory-model rewrite by
Pugh, Manson, Goetz and others) made `volatile` + the new happens-before
rules fix it: declare `helper volatile`, and the write inside the lock
happens-before every later read. The idiom is correct *only* with the
keyword; `final`-field initialization safety (JLS §17.5) covers the
immutable-fields case separately.

Modern guidance: DCL-with-volatile is correct but usually pointless —
`static` holder idiom (initialization-on-demand, JVM class-init lock does
the synchronization) or an enum singleton (Bloch, Effective Java Item 3)
achieve the same with zero ceremony.

## volatile vs synchronized vs AtomicX vs VarHandle

| Need | Tool |
|---|---|
| Flag / state bit visible across threads | `volatile boolean` |
| Publish an object graph once | `volatile` ref / `final` fields / static holder |
| Counter, accumulator | `AtomicLong` / `LongAdder` (not `volatile` + `++`) |
| Read-modify-write (CAS loops) | `AtomicReference.compareAndSet` |
| Mutual exclusion over compound actions | `synchronized` / `Lock` |
| Fine-grained ordering (acquire/release/opaque) | `VarHandle` modes |

`VarHandle` (Java 9) exposes what `volatile` bundles: `getVolatile`/
`setVolatile` (same as volatile access), `getAcquire`/`setRelease`
(cheaper one-directional edges), `getOpaque`/`setOpaque` (visibility without
ordering — progress without happens-before), `compareAndSet`/`getAndAdd`.
Rule: stay with `volatile` until a profiler or an algorithm (seekable atomic
index, sequence barriers à la Disruptor) forces you down a level.

## The volatile-Array Trap

`volatile int[] arr` makes the *reference* volatile; the *elements* are plain.
`arr[0] = 1` from one thread is invisible to others until some real edge
crosses. Element-level volatility needs `AtomicIntegerArray` (volatile
semantics per element via Unsafe intrinsics) or a `VarHandle` over the array
with `getVolatile`/`setVolatile`. This is a top-three volatile bug in the
wild — the keyword sits next to the type and reads like it covers the
contents.

## 64-bit Fields

JLS §17.7: implementations *may* split non-volatile `long`/`double`
accesses into two 32-bit halves (word tearing) — a reader can see half of
one write and half of another. In practice no HotSpot port tears, but the
*guarantee* exists only with `volatile`. Portable code never relies on
"works on my CPU" here.

## Key Invariants

1. Volatile write → later volatile read is a happens-before edge (with
   transitivity through program order on both sides).
2. `volatile` scales to exactly one access: compound actions need atomic
   classes or locks.
3. Reordering freedom ends at synchronization actions — the compiler/CPU may
   reorder anything *except* across these edges (roof of the JMM).
4. DCL is correct iff the field is volatile (or the holder idiom/enum is
   used instead).
5. Array volatility never extends to elements.
