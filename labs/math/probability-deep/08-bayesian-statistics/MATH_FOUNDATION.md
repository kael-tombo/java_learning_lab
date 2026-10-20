# Bayesian Statistics — Math Foundation

Numbers are pasted from executed runs (CODE_DEEP_DIVE.md carries the
transcripts); fractions exact, priors deliberate.

## 1. The Central Update, Fully Exhibited
Prior Beta(2, 2): mean 1/2, mode 1/2 (a symmetric, softly
middle-biased coin). Observing 7 heads, 3 tails:
posterior Beta(2+7, 2+3) = Beta(9, 5). Observed summaries: mean
9/14 ≈ 0.642857, mode (9−1)/(9+5−2) = 2/3. The run checked sequential-against-batch
updating — token-by-token versus whole-batch — and printed
`identical: True` for the same Beta(9, 5) endpoints.

## 2. What the Data Did to the Prior
Prior mean 1/2 → posterior mean 9/14: credibility rose because seven
of ten flips went heads, but only to 0.643, NOT to the raw 7/10. The
prior's four pseudo-observations (Beta(2,2) behaves like 4 imaginary
fair flips, half to each side) still drag on the mean. Mode 2/3 sits
higher than the mean: the update is right-skewed (B > ... asymmetry
from A,B asymmetry), and the two summaries disagree by design when the
posterior is asymmetric.

## 3. Predictive vs Plug-in — The Prior's Last Stitch
P(next head | data) = 9/14 (the posterior's own mean), compared with
the plug-in 7/10. Run printed the exact gap: 2/35 ≈ 0.0571. The
predictive is what the model TRULY anticipates for the next flip after
averaging over its posterior doubt; the plug-in answer is a single
coin pretending its parameter is known.

## 4. Normalization, in Factorial Arithmetic
The Beta(9, 5) density integrates to 1 because the beta-function
constant normalizes it: B(9, 5) = 8!·4!/13! — executed exactly as the
fraction 1/6435. So the posterior density is
6435 x^8 (1−x)^4 on [0, 1] — a fully explicit polynomial with machine-
verified constant.

## 5. Prior Sensitivity, Small Samples Side by Side
Same Bernoulli engine, three priors, three answers (all executed):
- Flat prior Beta(1, 1) on data TTT (all tails): posterior Beta(1, 4),
  mean = 1/5 = 0.2.
- Jeffreys prior Beta(1/2, 1/2) on data H, H, H, T: posterior
  Beta(7/2, 3/2), mean = 7/10.
- Beta(2, 2) on data HHT: posterior Beta(4, 3), mean = 4/7.
Flat priors add nothing — that is what flatness means; Beta(2,2)
injects half-a-coin conservatism into small reads; Jeffreys
(U-shaped, mass toward endpoints) is the least-commitment choice on
the logit scale. Prior choice is a modeling decision with distinct
numeric signatures — not private metaphysics.

## 6. Vocabulary the Runs Fixed
Beta(9, 5) (the central posterior), 9/14 (posterior mean and
predictive), 2/3 (posterior mode), 1/6435 (normalization constant),
2/35 (predictive-vs-plug-in gap), 1/5 and 4/7 (small-data alternative
posterior means), 7/10 (Jeffreys posterior mean). When these exact
figures appear later in QUIZ or interview contexts, they trace back to
printed lines above — the lab's claim of full auditability.
