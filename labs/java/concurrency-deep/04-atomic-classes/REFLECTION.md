# Reflection: Atomic Classes

## Recall without notes
1. State the lab's key fact (Every RMW linearizes at the winning CAS; losers retry (lock-free: some thread progresses, yours may starve); functions passed to getAndUpdate re-execute on retry (side-effect-free only; expect repeated runs under contention); ABA needs identity freshness/stamps/marks; LongAdder.sum() is a fuzzy non-atomic snapshot; weakCompareAndSet is retry-loops-only; two atomics cannot transact (multi-variable invariants need a lock or single packed CAS).) in under 40 words.
2. List the structures (`AtomicInteger.value` (volatile int) + `VALUE` field offset, Unsafe intrinsic `U.getAndAddInt` (= `lock cmpxchg` on x86), VarHandle-specified effects, CAS retry loop, (reference,stamp) pairs, `Striped64` cells + base with `@Contended` padding) and one API each from (`compareAndSet/compareAndExchange/weakCompareAndSet`, `getAndIncrement/getAndAdd/getAndUpdate/accumulateAndGet`, `AtomicStampedReference/AtomicMarkableReference`, `LongAdder.increment/sum/sumThenReset`, `LongAccumulator`, `DoubleAdder`) that touches them.

## Connect
3. Which invariant from THEORY.md did your STEP_BY_STEP.md probe demonstrate? Quote the probe output line that proves it.
4. Where does this lab's mechanism meet the neighboring lab (lifecycle<->monitors<->volatile<->atomics)? Name one concrete handoff (e.g. BLOCKED vs parking, unlock edge vs volatile edge, CAS vs lock for one counter).

## Challenge your intuition
5. Write the wrong version first (one COMMON_MISTAKES.md bug), predict its failure mode, then run it. Where did your prediction differ from the run?
6. Which of your predictions relied on timing or fairness? Restate it using only specified edges and invariants.

## Transfer
7. Name one place in your own codebase where lock-free read-modify-write via CAS: AtomicX, stamped references, and striped counters is assumed but unchecked. What single edge, guard change, or API swap would make it checkable?
8. What will you measure (PERFORMANCE.md harness) before claiming the fix helped?

## Exit ticket
- Two sentences: what breaks, and which source (`java.base/java/util/concurrent/atomic/AtomicInteger.java` (JDK 23), `Striped64.java` class javadoc, `VarHandle` specs, JSR-166 (2004, Doug Lea)) you would open first when it does.

## Count your retries (new prompts)
9. Quote your hand-loop retries-per-success at 1/2/8 writers; fit E[A] ≈ N by eye and state where saturation visibly begins.
10. Quote the rerun ratio (applications vs commits) from your contention run; name the cheapest line inside f that paid the multiplier.
11. Which shape were you running — cold sequence, hot metric, extremum, or enforcement total? State whether your counter pick matches the shape now.

## ABA diary
12. Write your Treiber interleaving as timestamped transitions (pop-A, pop-B, push-A, stale-CAS-win); then write the stamped replay with stamp values per step.
13. Price the stamp: Pair allocations per access on your hot path — measured or explicitly unmeasured with the reason stated.
14. Name one structure in your codebase with recycled node identity plus CAS; state its current ABA posture (fresh-alloc, stamped, marked, or exposed).

## Transfer extension
15. Find the hottest shared counter in your codebase; classify its writer count and state the AtomicLong-vs-LongAdder verdict with the crossover cited.
16. Find every `getAndUpdate`/`accumulateAndGet` lambda; mark pure vs effectful — each effectful one gets a post-commit refactor ticket.

## Exit-ticket extension
- One more sentence: the invariant (linearization, purity, fuzz, ABA, weak-loops-only) you violated most recently and the metric that exposed it.
- File your adder-crossover numbers (1/2/8/32 writers) as the lab's receipt.
- Name the effectful lambda you refactored this week and the before/after applications-vs-commits ratio.
