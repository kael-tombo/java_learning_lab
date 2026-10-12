# Quiz: Volatile Semantics

1. **State volatile's two guarantees and its famous non-guarantee.**
   A: Visibility (write happens-before later reads, JLS 17.4.5) + access atomicity incl. long/double. NOT compound-action atomicity: volatile++ races.

2. **Recite the four daily happens-before rules (JLS 17.4).**
   A: Program order within a thread; volatile write->later read; monitor unlock->later lock; start()->thread actions and thread actions->join(), plus executor submit->execute edges.

3. **Show the piggybacking chain in symbols.**
   A: write X -po-> write V -hb-> read V -po-> read X; transitivity makes read X see write X.

4. **Why was pre-2004 DCL broken, and what fixed it?**
   A: Reference publication could reorder before field initialization; JSR-133 (2004) + declaring the field volatile adds the write->read edge that orders construction before publication.

5. **Compare volatile costs on x86 vs ARM (qualitative).**
   A: x86 TSO: reads nearly free, writes pay a StoreLoad fence (xchg+lock). ARM/POWER: both directions need explicit fences (dmb ish). No portable numbers — qualitative only.

6. **What does `volatile int[]` make volatile?**
   A: The reference only; elements stay plain. Per-element volatility needs AtomicIntegerArray or VarHandle element access.

7. **What does JLS 17.7 permit for plain long/double?**
   A: Word tearing — split 32-bit halves can mix two writes. Only volatile (or atomics/locks) guarantees atomic access.

8. **When is VarHandle acquire/release/opaque preferable to volatile?**
   A: Almost never by default — only profiler-driven or algorithm-driven cases (sequence barriers). Default to volatile; descend deliberately.

## Scoring
- 7-8 correct: done. 5-6: re-read THEORY.md + INTERNALS.md. Below 5: redo STEP_BY_STEP.md before retrying.

9. **Draw the piggyback chain for publishing `{timeout, url}` behind `volatile ready`.**
   A: w(timeout), w(url), w(config) -po-> w(ready=true) -hb-> r(ready) -po-> r(config), r(timeout), r(url); transitivity delivers fully constructed reads.

10. **A config reload works on x86 but shows stale fields on ARM. What is missing?**
    A: An explicit edge the code never drew: x86 TSO supplied ordering for free that ARM requires as barriers — add the volatile publish/read pair (or lock) instead of tuning timing.

11. **Why does the DCL fast path read the volatile into a local first?**
    A: One volatile read per call instead of two (check + return) — halves fence cost on the hot path; the local re-check inside the lock keeps correctness.

12. **When is `final`-field safety (JLS 17.5) enough without volatile?**
    A: Immutable payloads reached via safe publication of the reference (holder idiom, volatile publish, enum): final stores are frozen at construction and visible to all readers of the reference.

13. **What breaks if the piggyback flag write moves before the payload writes?**
    A: The leftmost -po- link vanishes — the volatile edge still fires but no longer reaches the payload, so readers can legally see stale or half-written fields.

## After scoring
- For every miss, write the hb chain (or the colliding `++` schedule) in symbols before re-answering; prose without arrows does not stick for memory-model questions.
