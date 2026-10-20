# Lab 06 — Estimation Theory

Turns samples into science: how estimators are defined, judged
(bias, variance, MSE), pushed to consistency, and optimized
(likelihood, sufficiency).

## What This Lab Actually Teaches
- Bias, variance, and the exact identity MSE = Var + Bias²
  (THEORY.md).
- Consistency of estimator sequences and the MSE-to-zero proof path.
- MVUE and efficiency through the Cramer–Rao bound statement.
- Likelihood, maximum likelihood estimation, the invariance property,
  and asymptotic behavior at concept level.
- Sufficiency via the Neyman–Fisher factorization, with the Bernoulli
  count statistic as the worked case.
- Loss-driven location: squared loss vs absolute loss as executed
  minimizers.

## The Worked Material
MATH_FOUNDATION.md excavates one three-point sample (1, 2, 4): mean
7/3 anchored as exact squared-loss argmin (14/9 minimum, symmetric
25/16 flanks), median 2 as absolute-loss winner (risk 1 vs 10/9),
Bernoulli proportion bookkeeping (Bias 0, Var 1/40), the Uniform(0, 12)
max with bias −3 and the 4/3 cure, plus the seeded 200000-replication
simulation returning 8.997715881500072 against theory 9. Poisson MLE
= sample mean = 2 gets a derivative argument from first principles.
CODE_DEEP_DIVE.md pastes all captured outputs.

## Files (core six)
| File | Contents |
|------|----------|
| THEORY.md | Bias/MSE, consistency, MVUE, likelihood, factorization |
| MATH_FOUNDATION.md | Executed loss curves, MLE moments, uniform bias |
| CODE_DEEP_DIVE.md | Three runnable programs with real output |
| EXERCISES.md | Five problems with computed solutions |
| FLASHCARDS.md | 12 cards, statement cards for each core theorem |
| README.md | This overview |

Directory companions beyond the core six were left untouched.

## Suggested Sequence
1. THEORY.md definitions with the MSE identity read as the hub.
2. MATH_FOUNDATION.md with fractions session following along.
3. Run the three programs; watch the loss grid find 7/3 and the
   simulation agree with 9.
4. EXERCISES.md before its solutions.
5. FLASHCARDS.md until bias/factorization/invariance are word-perfect.
