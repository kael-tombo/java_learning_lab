# Lab 03 — Distributions

Catalogs the named probability families and makes every parameter a
computable object, exact where discrete and machine-precision where
smooth.

## What This Lab Actually Teaches
- PDF axioms (nonnegativity, unit mass) and the CDF relations
  F(x) = ∫ f, F'(x) = f at continuity points (THEORY.md).
- Why P(X = x) = 0 for continuous variables, and why density values
  themselves are not probabilities.
- Exact definitions and moments of Uniform(a, b), Exponential(λ),
  Binomial(n, p), Poisson(λ), Normal(μ, σ²).
- The uniqueness of exponential memorylessness, stated and then
  exhibited numerically.
- Φ via erf, and the engineered numbers behind the 68/95 folklore.

## The Worked Material
MATH_FOUNDATION.md runs the uniform cylinder round trip (F(1) = 1/2 and
derivative-back gives 1/2), exponential decimals to 17 digits
(e^{−1} = 0.36787944117144233 with the survival ratio e^{−0.5} =
0.6065306597126334 digit-matched), exact binomial tables —
Bin(4, 1/2) as [1/16, 1/4, 3/8, 1/4, 1/16] with E = np = 2,
Var = npq = 1, and Bin(10, 1/3) with P(X <= 1) = 2048/19683 — a full
Poisson(2) decimal table with truncation error 1.4e−06 disclosed, and
the erf-based normals (Φ(1) = 0.8413447460685428 etc.). CODE_DEEP_DIVE.md
pastes real captured output for all three programs.

## Files (core six)
| File | Contents |
|------|----------|
| THEORY.md | PDF laws, CDF relations, family definitions, memorylessness |
| MATH_FOUNDATION.md | Executed tables: uniform, exponential, binomial, Poisson, normal |
| CODE_DEEP_DIVE.md | Three runnable programs, real outputs pasted |
| EXERCISES.md | Five problems with worked, computed solutions |
| FLASHCARDS.md | 12 cards, one statement card per core theorem |
| README.md | This overview |

The directory's remaining companion files (QUIZ, HISTORY, sources,
tests, projects, and so on) were left as-is.

## Suggested Sequence
1. THEORY.md definitions, with the pdf-axiom subtleties read twice.
2. MATH_FOUNDATION.md tables side-by-side with a Python session.
3. Run the three CODE_DEEP_DIVE.md programs; recompute the normal
   percent rules from your own erf calls.
4. EXERCISES.md, solutions after attempts.
5. FLASHCARDS.md until family parameters and moments are instant.
