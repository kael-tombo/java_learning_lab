# Quiz: Atomic Classes

1. **What does AtomicInteger.incrementAndGet() compile to on JDK 23/x86?**
   A: `U.getAndAddInt(this, VALUE, 1) + 1` — one Unsafe intrinsic on the VALUE field offset, one `lock cmpxchg`-family instruction, with VarHandle-specified effects.

2. **Write the CAS loop and name its linearization point.**
   A: `do { p = get(); n = f(p); } while (!compareAndSet(p, n));` Linearization = the winning CAS; losers retry with fresh reads.

3. **Why must getAndUpdate functions be pure?**
   A: f runs outside the CAS and re-executes per retry (~3x observed under contention) — side effects repeat.

4. **compareAndSet vs compareAndExchange vs weakCompareAndSet?**
   A: CAS->boolean verdict; CE->witness value (retry from it, skip re-read); weak->boolean allowed spurious failure, loops-only, never one-shot.

5. **What is ABA and when does it bite?**
   A: Value A->B->A passes CAS equality while history changed; bites where transitions matter (reused nodes in lock-free stacks). Fix: fresh allocation, AtomicStampedReference (int stamp), or AtomicMarkableReference (boolean).

6. **Why is LongAdder.sum() fuzzy?**
   A: It walks base + cells with no lock; concurrent increments during the walk are missed or double-counted. Metrics yes, money no.

7. **AtomicLong vs LongAdder: the decision rule?**
   A: ~2-4 writers crossover: below, AtomicLong (cell overhead otherwise); above, LongAdder striping. sum() exactness needs quiescence (sumThenReset).

8. **Why can't two atomics transact?**
   A: Sequential sets expose an intermediate state; invariants spanning variables need one lock or one packed single-CAS word.

## Scoring
- 7-8 correct: done. 5-6: re-read THEORY.md + INTERNALS.md. Below 5: redo STEP_BY_STEP.md before retrying.

9. **What does `U.getAndAddInt(this, VALUE, 1)` buy over a synchronized increment?**
   A: One `lock cmpxchg`-family instruction with volatile effects: no monitor, no park, no BLOCKED — uncontended ~10-20ns on x86 with retry-instead-of-wait under contention.

10. **Function applications exceed commits 3:1 in your metrics. Bug or normal?**
    A: Normal for effectful `getAndUpdate` under contention (re-execution per lost race) — the bug is the side effect inside f; move it after the commit and the ratio stops mattering.

11. **When is `weakCompareAndSetVolatile` correct, and when is it a bug?**
    A: Correct only inside retry loops (spurious failure costs one lap, real on ARM/LL-SC); a one-shot boolean test on weak CAS is a correctness bug — use plain `compareAndSet`.

12. **How do you prove `sum()` fuzz on your own JVM?**
    A: `sum()` concurrent with increments vs `sum()`/`sumThenReset()` at a quiescent point: divergence that vanishes at rest is the specified fuzz — metrics-only verdict confirmed by the pair.

13. **Two halves of one `AtomicLong` vs two `AtomicInteger`s for a paired invariant?**
    A: Packed halves commit in one CAS (no torn pair observable); two atomics expose the intermediate state — pack within bit budget, lock beyond it.

## After scoring
- For every miss, run the proving snippet (hand loop, rerun counter, ABA demo, adder race) and paste the verdict line — atomics knowledge without a run is untested bravado.
