# Flashcards: Atomic Classes

Q: AtomicInteger mechanics (JDK23)? | A: volatile int value + VALUE offset; U.getAndAddInt intrinsic = one lock cmpxchg.
Q: CAS loop shape? | A: do { p=get(); n=f(p); } while(!CAS(p,n)); linearize at winning CAS.
Q: Update-fn purity? | A: Required — f re-runs per retry (~3x under contention).
Q: CAS vs CE vs weak? | A: boolean verdict / witness value / spurious-failure loops-only.
Q: ABA in one line? | A: A->B->A passes equality; history-sensitive structures corrupt.
Q: ABA fixes? | A: Fresh allocation, AtomicStampedReference (stamp), AtomicMarkableReference (mark).
Q: LongAdder structure? | A: base + hashed Cell[] stripes; sum() = fuzzy walk, non-atomic.
Q: Adder vs AtomicLong rule? | A: Crossover ~2-4 writers; below AtomicLong, above Adder.
Q: sum() use? | A: Metrics/dashboards only; never money/quotas/bounds.
Q: Two-atomics transaction? | A: Impossible — intermediate state visible; use lock or packed single CAS.

## Method
- Cover the A column; recall aloud; check. Cycle missed cards twice before finishing.

## More cards (same deck)
Q: `incrementAndGet` source line (JDK 23)? | A: `U.getAndAddInt(this, VALUE, 1) + 1` — intrinsic on the VALUE offset.
Q: `VALUE` offset meaning? | A: Static final field offset locating `value` for Unsafe/VarHandle access.
Q: Linearization point of a CAS loop? | A: The single winning CAS — history orders by winners.
Q: Loser threads' effect? | A: None — fresh read plus retry; only winners mutate history.
Q: `haveNext` optimization (JDK source)? | A: Skips re-applying f when the re-read matches — fewer function runs, same contract.
Q: `compareAndExchange` retry shape? | A: `prev = witness; retry` — skips one volatile re-read per failed lap.
Q: Spurious failure platforms? | A: Real on ARM/LL-SC, absent on x86 — loops-only rule covers both.
Q: Treiber stack + plain CAS hazard? | A: Popped-node reuse lets A->B->A fool CAS — corrupt `next` linkage silently.
Q: `AtomicMarkableReference` payload? | A: (reference, boolean) pair — one-bit deleted-or-not marking, cheaper than stamps.
Q: `sumThenReset` use? | A: Quiescent-point metrics drain — exact only when no concurrent updates.
Q: `LongAccumulator` identity role? | A: Seed for the fold (e.g. max starts at MIN_VALUE) — wrong seed corrupts the extremum.
Q: `@Contended` width and flag? | A: 128-byte padding cells; user code needs `-XX:-RestrictContended` to apply it.

## Drill
- Recite the CAS loop from memory with the linearization sentence attached — no loop without its commit point.
- For every ABA card, narrate the A->B->A transition schedule aloud before flipping.
- Sort five counter shapes (flag, cold counter, hot counter, max-track, money total) into AtomicLong/LongAdder/LongAccumulator/locked-total without hesitation.
- Retire a card only after three consecutive clean recalls across two sittings.
