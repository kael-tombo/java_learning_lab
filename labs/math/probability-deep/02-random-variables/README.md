# Lab 02 — Random Variables

Turns sample spaces into number-generation devices and builds the
moment machinery (expectation, variance, CDF) on exact fractions.

## What This Lab Actually Teaches
- Random variables as measurable bookkeeping, and the pushed-forward
  distribution that encodes everything about them (THEORY.md).
- PMF axioms, CDF definition with its nondecreasing/right-continuous
  structure, and the two-way CDF ↔ PMF relation via summation.
- Expectation of functions (LOTUS), linearity of expectation with its
  independence-free hypothesis, the Var = E[X^2] − (EX)^2 identity.
- Joint PMFs, marginalization, and the product rule for independence.

## The Worked Material
MATH_FOUNDATION.md executes the two-dice sum table (P(2) = 1/36,
P(7) = 1/6, mass 1 machine-checked), its moments E = 7, E[X^2] = 329/6,
Var = 35/6 confirmed by both routes on the same run, a three-point CDF
with jumps read back into the pmf, a live LOTUS counterexample
(E[1/X] = 3/4 vs 1/E[X] = 2/3), single-die moments (7/2, 91/6, 35/12),
and conditional/accumulated reads (P(X = 7 | odd) = 1/3, F(7) = 7/12).
CODE_DEEP_DIVE.md carries the runnable programs with captured output.

## Files (core six)
| File | Contents |
|------|----------|
| THEORY.md | Measurability, pushforward, CDF/PMF, moments, linearity |
| MATH_FOUNDATION.md | Executed dice moments, CDF jumps, LOTUS trap |
| CODE_DEEP_DIVE.md | Three exact-arithmetic programs and their output |
| EXERCISES.md | Five problems with computed solutions |
| FLASHCARDS.md | 12 cards, theorem-statement cards included |
| README.md | This overview |

Files beyond the core six in this directory keep their original
content and were untouched by this pass.

## Suggested Sequence
1. THEORY.md, tracking each definition's role in the arithmetic to come.
2. MATH_FOUNDATION.md next to a fractions REPL — re-derive each printed
   fraction yourself before reading the next block.
3. Run the three CODE_DEEP_DIVE.md programs; the mocks (total mass,
   equal-variance-routes checks) should pass unmodified.
4. EXERCISES.md problems first, solutions second.
5. FLASHCARDS.md until the statement cards come out verbatim.
