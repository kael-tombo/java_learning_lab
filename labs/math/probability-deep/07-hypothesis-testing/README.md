# Lab 07 — Hypothesis Testing

Builds the two-error architecture of statistical tests and prices
every decision with exact fractions on deliberately tiny samples.

## What This Lab Actually Teaches
- Null/alternative, test statistic, rejection region, and the exact
  definitions of Type I and Type II errors (THEORY.md).
- Size alpha as a designed constant; power 1 − beta as a curve over
  the truth; the constitutional asymmetry between the two.
- Exact binomial tests: region sizes as coefficient sums over 2^n.
- The p-value defined rigorously — a tail probability under H0, never
  a probability on hypotheses.
- Permutation tests as exactness by construction, with exhaustive
  label-space enumeration on 3v3 and 4v4 samples.

## The Worked Material
MATH_FOUNDATION.md prices the two-sided region {k <= 1} ∪ {k >= 9} at
exactly 22/1024 = 11/512, computes Type II at true p = 3/10 as
4252739841/5000000000 = 0.8505479682 (power 0.1494520318, mirror-equal
at 7/10 — run certified), prices the one-sided region at 7/128, and
executes exhaustive permutation tests: 1/20 one-sided and 1/10
two-sided at 3v3, 1/35 two-sided at 4v4. CODE_DEEP_DIVE.md carries
three programs with captured outputs, all exact.

## Files (core six)
| File | Contents |
|------|----------|
| THEORY.md | Errors, size, power, p-values, permutation exactness |
| MATH_FOUNDATION.md | Exact region pricing and permutation counts |
| CODE_DEEP_DIVE.md | Three runnable programs, outputs as captured |
| EXERCISES.md | Five problems with computed solutions |
| FLASHCARDS.md | 12 cards, definition- and number-grounded |
| README.md | This overview |

Companion files in this directory were untouched by this pass.

## Suggested Sequence
1. THEORY.md, pausing on the p-value paragraph twice.
2. MATH_FOUNDATION.md with fractions and itertools open.
3. Run the three programs; confirm each printed fraction and count.
4. EXERCISES.md, solutions after attempts.
5. FLASHCARDS.md until Type I/II and p-value definitions are verbatim.
