# Debugging: Atomic Classes

## Capture
- Code search: `getAndUpdate/accumulateAndGet` lambdas with side effects; one-shot `weakCompareAndSet`; `sum()` used as exact total; two-atomic "transactions".
- Metrics: retry rate (instrument CAS failures per op), contention queue depth, CPU burn vs throughput curve.

## Decode symptoms
- Duplicated effects (double logging, double enqueue) -> side-effecting update function re-run (~3x under contention).
- Spurious "lost race" branches -> one-shot weak CAS misread.
- Torn multi-field state -> two-atomic commit mistaken for atomic.
- Throughput cliff past a few writers -> single CAS word saturated; stripe with LongAdder.
- Money/quota drift -> fuzzy `sum()` treated as exact.

## Triage recipe
1. Reproduce under contention (more writers than ~2-4) and count retries per success; linear growth confirms the hot word.
2. Replace effects-inside-`f` with pure `f` + post-commit effect; re-measure.
3. For ABA suspects, log identity transitions (A->B->A) and switch to stamped/markable or fresh allocation.
4. Verify padding only after measuring (`-XX:+PrintFieldLayout`, perf counters); 128-byte cells cost real memory.

## Five-minute checklist
- [ ] Update fns pure? [ ] weak CAS loop-only? [ ] No two-atomic transactions? [ ] sum() metrics-only? [ ] ABA addressed where identity matters?

## Sources
- `java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea). Keep THEORY.md open; every diagnosis ends by naming the violated invariant.

## Retry-rate instrumentation (the core metric)
- Wrap the CAS loop with a failure counter (failed `compareAndSet` per successful commit): linear growth of retries-per-success with writer count confirms the hot single word — the curve from MATH_FOUNDATION.md made observable.
- Alert threshold: retries-per-success climbing past ~N (writer count) means saturation — the word is the bottleneck, not the function body; stripe before optimizing the function.
- After striping (`LongAdder`), the same counter should collapse toward ~1 per commit: unchanged retry rates after the swap mean the contention moved (or was never the word) — re-profile instead of celebrating.

## Side-effect duplication forensics
- Doubled log lines, double enqueues, or inflated side counters under load with exact final totals: the update function re-ran on lost CAS races (~3x observed in CODE_DEEP_DIVE.md snippet 2) — pure final value, repeated effects.
- Confirm by counting function applications vs commits (snippet 2's `applications` counter): applications > commits proves re-execution; the fix is pure `f` plus a post-commit effect, never deduplication downstream.
- Audit every `getAndUpdate`/`accumulateAndGet` lambda for I/O, logging, counter bumps, and collection mutation — each is a repeatable effect until moved after the commit.

## ABA suspect workup
- Lock-free stack/pool corruption where values look right but links are wrong: log identity transitions (A -> B -> A on the same reference) around the CAS — a successful `compareAndSet(A, C)` across a B-visit is the positive ID.
- Fix ladder in cost order: fresh allocation per offer (GC-backed identity freshness, the CLQ trick) first; `AtomicStampedReference` (stamp++ per mutation) where reuse is structural; `AtomicMarkableReference` for deleted-or-not marking.
- Stamped-reference cost check: a `Pair` allocation per access — profile before and after; stamps on cold paths are pure overhead, on Treiber-style hot paths they are the correctness condition.

## Fuzzy-sum incidents
- Dashboard/money drift where increments are exact but reports skew: `sum()` walked base + cells mid-mutation — concurrent updates during the walk are missed or double-counted by specification.
- Confirm by comparing racy `sum()` against a quiescent `sum()` (or `sumThenReset` at a quiet point): divergence that vanishes at rest is fuzz, not loss — enforce from exact sources (`AtomicLong`, locked totals), keep adder sums for metrics.
- `LongAccumulator` (max/min tracking) has the same walk semantics: identity-element seeding plus concurrent updates means the extremum is "seen during the walk", never a transaction.
