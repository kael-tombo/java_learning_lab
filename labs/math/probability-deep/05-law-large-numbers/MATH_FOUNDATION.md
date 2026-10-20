# Law of Large Numbers — Math Foundation

Numbers are run outputs (transcripts inside CODE_DEEP_DIVE.md): exact
fractions for the Bernoulli bookkeeping, seeded simulation values
reproduced as printed.

## 1. The 1/n Clock on a Concrete Mean
For Bernoulli(1/2) summands, Var(X_n) = 1/(4n). Observed exact table:
n = 1 → 1/4; n = 4 → 1/16; n = 16 → 1/64; n = 64 → 1/256;
n = 256 → 1/1024. Every quadrupling of n quarters the variance — the
shrinkage schedule of the whole lab, in four lines.

## 2. Chebyshev Bound vs Exact Avstract Probability
At n = 4 and threshold c = 1/2: the event |X_4 − 1/2| >= 1/2 means the
sample mean sits at 0 or 1 — probability 2/16 = 1/8 (exact). The bound
computes Var/(c^2) = (1/16)/(1/4) = 1/4. Run verdict: `valid bound:
True` with 1/8 <= 1/4 — the inequality holds while wasting a factor of
two. Bounds are guarantees, not estimates.

## 3. The Vacuous Case Done Right
Threshold c = 3/4 at n = 4: the event is empty (X_4 lives in [0, 1],
so |X_4 − 1/2| >= 3/4 requires the mean below −1/4 or above 5/4).
Exact probability: 0. The Chebyshev number (1/16)/(9/16) = 1/9 is still
a valid envelope — 0 <= 1/9 — even though it wastes everything. A
bound that stays correct when the event is impossible has no hidden
hypotheses.

## 4. Seeded Simulation — The Clock in Action (observed as printed)
Seed 2024, Bernoulli(1/2) sample means:
n = 10: mean 0.600000, |dev| 0.100000
n = 100: mean 0.580000, |dev| 0.080000
n = 10000: mean 0.494700, |dev| 0.005300
n = 1000000: mean 0.500447, |dev| 0.000447
Deviation shrinks by orders of magnitude as n grows; at the last line
the empirical mean sits within 4.5e−04 of 1/2, inside the σ/√n scale
(1/(2·1000) = 0.0005 for a million flips).

## 5. When the Hypothesis Matters — Heavy Tails Live
Summands take 1, 2, 3 or 10^6 with weights (45, 30, 20, 5) percent.
Observed running means (printed):
first 200: 45001.6350; first 2000: 45001.6325; first 20000: 49151.6488;
first 200000: 49736.6496.
The mean is 0.5% off target after 200000 draws — slower by orders of
magnitude than the Bernoulli case at comparable n. Finite mean makes
the strong law TRUE here, but the size of rare 10^6 jumps hosts the
fluctuation budget: variance hypothesis or not, rates differ wildly.

## 6. Markov and Chebyshev Against the True Tail
Exponential(1): exact P(X >= 3) = e^{−3} = 0.049787068367863944.
Markov grants P <= E[X]/3 = 1/3 and Chebyshev grants
P(|X − 1| >= 2) <= Var/t^2 = 1/4. Both envelopes are honest — 1/3 and
1/4 versus the true 0.0498 — illustrating tail bounds as safety nets,
two orders of magnitude above the supermarket price of the truth.
