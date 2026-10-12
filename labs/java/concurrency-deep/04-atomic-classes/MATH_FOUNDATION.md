# Math Foundation: Atomic Classes

## Linearization
- Each RMW linearizes at its winning CAS: history ≡ sequential order of winning CASes. Losers have no effect (fresh read + retry), so correctness = proving the CAS-success condition (value still prev) implies the sequential spec.

## Retry geometry (defensible formula)
- Contended single word, N symmetric writers, per-attempt collision probability p ≈ (N-1)/N under saturation: attempts-to-success A ~ Geometric(1-p), E[A] = 1/(1-p) ≈ N. Worked: N=2 -> ~2 attempts; N=8 -> ~8; N=32 -> ~32 per commit. Per-thread CPU per commit grows ~linearly in N while system commits stay ~flat — the curve that justifies striping. (Model assumes saturation; uncontended p≈0 -> E[A]≈1.)

## Striping arithmetic
- LongAdder with S live cells: collision probability per attempt ≈ 1/S of the single-word case (hash spread), so E[A] ≈ 1 + (N-1)/S roughly. Worked: N=32 writers, S=16 cells -> E[A] ≈ 1 + 31/16 ≈ 2.9 vs ≈32 unstriped — order-of-magnitude fewer retries. sum() cost O(S) with fuzz window = walk duration.

## Amdahl-adjacent bound
- Fraction s of increments serialized on one word caps speedup ≤ 1/(s + (1-s)/N) → 1/s as N grows; striping shrinks s by spreading serialization across S cells. Use to explain the measured crossover (~2-4 writers), not to predict exact ops/s.

## Rule
Every formula above is defended in plain words beside it. No formula here predicts wall-clock time — all bound orderings, counts, or scaling shapes.

## Retry expectation, derived step by step
- Model: N symmetric writers saturated on one word; each attempt collides with probability p ≈ (N-1)/N (some rival commits first with N-1 rivals racing).
- Attempts-to-success A ~ Geometric(q = 1-p): P(A=k) = (1-q)^(k-1)·q, E[A] = 1/q = 1/(1-p) ≈ N — mean laps per commit scale with writers.
- Worked: N=2 -> E[A] ≈ 2; N=8 -> E[A] ≈ 8; N=32 -> E[A] ≈ 32 — per-thread CPU per commit grows ~linearly while system commits stay ~1 per CAS latency (lock-free: someone always wins, you may wait).
- Uncontended limit: p ≈ 0 -> E[A] ≈ 1 — one CAS (~10-20ns x86), which is why cold atomics beat locks and hot single-word atomics lose to striping.
- Saturation assumption stated: below saturation p < (N-1)/N and E[A] < N — the formula bounds the bad case; measurement picks the crossover (~2-4 writers).

## Striping gain, worked twice
- S live cells, N writers, hash spread: per-attempt collision ≈ 1/S of the single-word case — E[A] ≈ 1 + (N-1)/S roughly.
- Worked: N=32, S=16 -> E[A] ≈ 1 + 31/16 ≈ 2.9 vs ≈ 32 unstriped — an order of magnitude fewer laps per commit.
- Worked small: N=8, S=4 -> E[A] ≈ 1 + 7/4 ≈ 2.75 vs ≈ 8 — striping pays well before the extreme case, matching the measured crossover.
- `sum()` cost O(S) with fuzz window = walk duration: concurrent increments during the walk are missed or double-counted — exactness requires quiescence, priced as waiting for quiet.

## Amdahl bound on one word
- Fraction s of the increment path serialized on the word: speedup(N) ≤ 1/(s + (1-s)/N) -> 1/s as N grows — one word caps throughput no matter the core count.
- Striping shrinks s by spreading serialization across S cells: effective bound rises ~S-fold for the write path while the read path (`sum()`) stays fuzzy — throughput bought with read precision.
- Packing corollary: two 32-bit halves in one `AtomicLong` share one s — one CAS commits both, so multi-field atomicity is bought with bit budget, not with extra words.

## Rerun multiplier, bounded honestly
- Function f runs once per attempt: applications ≈ commits × E[A] — at E[A] ≈ 3 under contention (snippet 2's measured ~3x), a logging f triples its I/O cost silently.
- `haveNext` trims re-application when the re-read matches, so measured ratios sit below E[A] for cheap f — the bound is applications ≤ commits × E[A], not equality.
- Design inequality: cost(f) × E[A] must stay below the lock-based alternative per op, else the "lock-free" loop is dearer than the monitor — retry multiplies function cost, not just CAS cost.
