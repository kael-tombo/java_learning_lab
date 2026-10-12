# Exercises: Atomic Classes

## 1. CAS loop by hand (20 min)
Build `incrementIfEven(AtomicInteger)` with an explicit `get/compareAndSet` loop; stress with 8 threads and show exact totals. Print retries-per-success to see the geometric curve. APIs: `get/compareAndSet`.

## 2. Side-effect rerun proof (15 min)
`getAndUpdate(x -> { counter++; return x+1; })` under contention; show the inner counter exceeding commits (~3x in the lab dive). Refactor to pure function + post-commit effect; show equality restored.

## 3. compareAndExchange witness (15 min)
Rewrite exercise 1 with `compareAndExchange` retrying from the witness instead of re-reading. Measure or reason: one fewer volatile read per failed lap.

## 4. ABA construction (25 min)
Treiber-stack sketch with node reuse: interleave pop-A, pop-B, push-A so a stale `compareAndSet(A, C)` succeeds on the "wrong A". Fix with `AtomicStampedReference` (stamp++ per mutation) and show the stale CAS now fails.

## 5. Adder crossover (20 min)
JMH or hand harness: `AtomicLong.incrementAndGet` vs `LongAdder.increment` at 1/2/8/32 writers. Find your machine's crossover (~2-4 writers); show `sum()` fuzz by summing concurrent with increments vs at a quiescent point.

## Submission checklist
- [ ] Each task ran on your JVM with output pasted. [ ] Predictions written before runs. [ ] One deliberate break-and-fix per lab recorded.

## 6. False-sharing probe (20 min)
Task: place two `AtomicLong` counters adjacent (array or neighboring fields) vs padded apart; hammer both from distinct threads and compare ops/s.
Check: explain the gap via cache-line ping-pong (same line invalidated per CAS) and confirm layout with `-XX:+PrintFieldLayout`; then note why `LongAdder` cells ship `@Contended`-padded by default.
APIs: `AtomicLong`, `PrintFieldLayout`, hand harness; success = the layout quoted and the padding decision justified by measurement, not assumed.

## 7. Packed single-word transaction (20 min)
Task: pack two 32-bit counters into one `AtomicLong` (hi/lo halves); update both halves with one CAS loop and show no observable intermediate state under a concurrent reader.
Check: contrast with two-`AtomicInteger` updates showing torn pairs; state the packing limit (bit widths, overflow discipline) that bounds the trick.
APIs: `AtomicLong.compareAndSet`, bit shifts/masks; success = torn-pair demo plus exact packed demo, with the width budget written down.

## 8. Weak-CAS loop audit (15 min)
Task: convert the exercise-1 loop to `weakCompareAndSetVolatile`; stress at 4 threads and show exact totals, then deliberately use weak CAS as a one-shot test and characterize the spurious-failure hazard.
Check: state the rule (loops-only, never one-shot verdicts) and note where the platform matters (spurious failures real on ARM/LL-SC, absent on x86 — correct on both only inside loops).
APIs: `weakCompareAndSetVolatile`, `compareAndSet`; success = exact loop totals plus the one-shot failure mode named.

## Submission additions
- [ ] Retries-per-success numbers quoted for the hand loop (exercise 1) at your thread count.
- [ ] Side-effect rerun ratio (applications vs commits) pasted from exercise 2 style counting.
- [ ] ABA interleaving schedule written as transitions (pop-A, pop-B, push-A, stale-CAS) with the stamped fix verdict.
- [ ] Adder crossover point (1/2/8/32 writers) with your machine's numbers.
- [ ] One deliberately impure update function with the duplication failure recorded.
