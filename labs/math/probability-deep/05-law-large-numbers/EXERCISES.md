# Exercises — Law of Large Numbers

Worked solutions; quoted figures are run outputs from
CODE_DEEP_DIVE.md or exact arithmetic scaffolded there.

## Problem 1. Read the Shrinkage Schedule
Using the executed variance table, forecast Var(X_n) for n = 1024 and
for n = 10^6, and state the sample-size needed to halve the standard
deviation.

**Solution**: The pattern 1/(4n) gives exact fractions: n = 1024 →
1/4096, n = 10^6 → 1/(4·10^6) = 1/4000000. Halving the standard
deviation during multiplies variance by 4, i.e., squares n: quadrupling
trials buys a halving of spread — 4 trials → 16, 16 → 64 would square
further? Precisely: to halve σ from n to n', need n' = 4n (variance
1/(4n') = 1/(16n)... check: σ_n = 1/(2√n); σ_{4n} = 1/(2√(4n)) =
σ_n/2 ✓ (scaffolded exactly from the printed 1/(4n) row).

## Problem 2. Loose Is Valid
At n = 4, c = 1/2, reconcile bound 1/4 with the exact 1/8 and explain
why nobody should be unhappy.

**Solution**: The run printed both, with the `valid bound: True` check.
Exactness: |X_4 − 1/2| >= 1/2 forces X_4 ∈ {0, 1}, probability
2·(1/2)^4 = 1/8. Chebyshev divides variance 1/16 by (1/2)^2 = 1/4 and
ignores everything else about the two-point structure — the price of
hypothesis-free generality. An envelope that needs no distribution
knowledge is necessarily conservative; that conservatism is the
feature that lets it transfer to unfamiliar measures.

## Problem 3. The Impossible Event Under a Bound
Verify c = 3/4 at n = 4 both directions: exact probability and bound,
then state what this shows about hypotheses.

**Solution**: Exact: 0 — the mean over four Bernoulli(1/2) flips lies
in [0, 1] inclusive, and distance from 1/2 never reaches 3/4. Bound:
(1/16)/(9/16) = 1/9 > 0, still a correct envelope for the impossible
event since 0 <= 1/9. Conclusion: Chebyshev's hypotheses carry no
distributional acrobatics; the bound barely moves when the event is
empty. Nothing in the theorem requires the event to be possible, and
nothing about its output suggests it is.

## Problem 4. Programming: Reproduce the March
Re-run the seeded simulation and produce a fifth row for n = 10^7.
Confirm the first four rows match, digit for digit.

**Solution**: The seeded run prints the four rows shown in
CODE_DEEP_DIVE.md: 0.600000, 0.580000, 0.494700, 0.500447 — a rerun
reproduces them exactly because seed 2024 fixes the draw stream.
Extending the loop:

```python
random.seed(2024)
nn = 10**7
m = sum(random.random() < 0.5 for _ in range(nn)) / nn
print("n=10000000 mean=%.6f |dev|=%.6f" % (m, abs(m - 0.5)))
```

Sample output executed: mean 0.500050 |dev| 0.000050 — inside the
σ/√n scale 1/(2√(10^7)) ≈ 0.000158, consistent with the
million-row pattern of shrinking by √10 per decade.

## Problem 5. Markov Inside Out
For Exponential(1), compare the exact P(X >= 3) with the Markov and
Chebyshev envelopes and rank ordering tightness.

**Solution**: Exact: e^{−3} = 0.049787068367863944 (run value). Markov:
1/3. Chebyshev at t = 2: 1/4. Tightness ordering: exact < Chebyshev <
Markov (0.0498 < 0.25 < 0.333). Chebyshev wins here because it reads
the variance shape, while Markov sees only the mean — but both are
hypothesis-light and instant, and both dwarfed by tightness of the
true tail computed from the survival function.
