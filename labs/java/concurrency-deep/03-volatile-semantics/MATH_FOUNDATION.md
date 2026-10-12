# Math Foundation: Volatile Semantics

## Edge calculus (JLS 17.4)
- Rules: (po) program order; (vol) write(V) -hb-> read(V) for later reads; (mon) unlock(M) -hb-> lock(M); (life) start()->
  actions, actions ->join(). Closure: hb is transitive; po + hb compose. Correctness proof = exhibiting the chain.
- Piggyback theorem: w(X) -po-> w(V) -hb-> r(V) -po-> r(X) ⟹ r(X) observes w(X) (or a later write). Any publication argument must match this shape with statement order as written.

## Why volatile++ must lose (counting)
- Increment = 3 steps (r, +1, w) with no edge between threads: N threads x K increments admit interleavings where two threads read the same value and one update is lost per collision. Expected loss grows with overlap window; exact total requires CAS (AtomicLong) or striping (LongAdder) — no closed form needed, the race is structural.

## Fence-cost ordering (qualitative, defensible)
- x86 TSO: cost(read-vol) ≈ cost(read-plain) < cost(write-vol) ≈ cost(uncontended-CAS) ≈ tens of ns. ARM: cost(read-vol) > plain, cost(write-vol) > x86 write-vol (explicit dmb ish both ways). Inequalities only — never cite portable constants.

## DCL correctness condition
- Correct ⟺ (field volatile ∧ check-then-lock-then-recheck shape) ∨ holder-idiom ∨ enum. Plain-field DCL has a legal JMM execution publishing the reference before field stores — one counterexample execution suffices to declare it broken.

## Rule
Every formula above is defended in plain words beside it. No formula here predicts wall-clock time — all bound orderings, counts, or scaling shapes.

## Piggyback proof, line by line
- Program order (writer): w(config.timeout) -po-> w(config.url) -po-> w(config) -po-> w(ready=true) — all plain writes sequenced before the volatile write in source order.
- Volatile edge: w(ready=true) -hb-> r(ready==true) for the reader's later read — JLS 17.4.5, the single cross-thread arrow.
- Program order (reader): r(ready) -po-> r(config) -po-> r(config.timeout) — everything after the volatile read is ordered after it.
- Transitivity composes all three: w(config.timeout) -hb-> r(config.timeout) — the reader's `timeout == 5000` assertion is a theorem, not an observation.
- Order-swap counterexample: moving w(ready=true) before the payload writes breaks the leftmost -po- link — the chain no longer reaches the payload, and staleness becomes legal.

## Loss counting for volatile++ (structural, with numbers)
- Increment = r, +1, w with a collision window between r and w: with N threads × K increments, each overlap of two windows on equal values loses exactly one update.
- Worked scale from snippet 2: 8 threads × 500,000 = 4,000,000 expected; measured shortfall is routinely six figures — the loss fraction grows with overlap, which grows with N and with window width.
- No closed form is needed for the verdict: any schedule with ≥ 1 collision loses ≥ 1 update, and collisions are unavoidable without mutual exclusion — the race is structural, proved by exhibiting one colliding schedule.
- Fix comparison: `AtomicLong` closes the window with one CAS (exact, ~10-20ns uncontended); `LongAdder` dissolves the window by striping (exact sum at rest, fuzzy mid-flight) — both remove collisions rather than outrunning them.

## Fence-cost inequalities (defensible, portable)
- x86 TSO: cost(read-vol) ≈ cost(read-plain) < cost(write-vol) ≈ cost(uncontended-CAS) — one ordering of three quantities, qualitative.
- ARM weak model: cost(read-vol) > cost(read-plain-x86-baseline) and cost(write-vol) > cost(write-vol-x86) — explicit `dmb ish` both ways; inequalities only, never constants.
- Publication batching math: k payload fields + 1 volatile flag = k plain writes + 1 fence — amortized fence cost per field = 1/k of a fence; batching is division.
- DCL fast-path math: local-variable read shape = 1 volatile read per call vs 2 without the local — halves fence cost on the hot path for free.

## Tearing probability vs guarantee
- JLS 17.7 permits word tearing for plain long/double: the spec-legal execution set includes half-mixed values — P(observe tear) > 0 in the model even where HotSpot never tears in practice.
- `volatile` (or AtomicLong/lock) shrinks the legal set to whole values only: P(tear) = 0 by specification on every JVM, every CPU — portability is a proof about the set, not a measurement on one machine.
