# Lab 01 — Probability Axioms

Builds exact probability reasoning on a finite sample space and shows
the axioms at work with rational numbers rather than gestures.

## What This Lab Actually Teaches
- The probability-space triple (Ω, F, P) and the three Kolmogorov
  axioms in their exact statements (THEORY.md).
- The theorem inventory that falls out for free: complement rule,
  monotonicity, inclusion–exclusion, union bound.
- Conditional probability as rescaling a surviving set of outcomes.
- Law of total probability over a partition, and Bayes' inversion of
  conditioning.
- Independence as a failed product equality, P(A ∩ B) =? P(A) P(B).

## The Worked Material
MATH_FOUNDATION.md runs one die model exhaustively in exact fractions:
P(A ∪ B) = 5/6 by two routes, the conditional rescaling that turns
{1,2,3} into weights (1/3, 1/3, 1/3), a live-total reassembly
(1/2 · 1/3 + 1/2 · 2/3 = 1/2), and the medical-test block where
P(D | +) = 99/297 = 1/3 against the naive 99/101. CODE_DEEP_DIVE.md
provides runnable Python (stdlib fractions, math, random) whose printed
outputs were captured and pasted — no hand-derived figures anywhere.

## Files (core six)
| File | Contents |
|------|----------|
| THEORY.md | Exact statements: axioms, conditioning, Bayes, independence |
| MATH_FOUNDATION.md | Executed Venn, partition, and test arithmetic |
| CODE_DEEP_DIVE.md | Three snippets with real captured output |
| EXERCISES.md | Five problems, each with a computed solution |
| FLASHCARDS.md | 12 cards including axiom- and Bayes-statement cards |
| README.md | This overview |

Other files in this directory (QUIZ, HISTORY, ARCHITECTURE, source and
tests, etc.) are companion material and were not part of this rewrite.

## Suggested Sequence
1. THEORY.md end to end — statements first, mechanics second.
2. MATH_FOUNDATION.md with a fractions-enabled REPL alongside.
3. Run the three CODE_DEEP_DIVE.md programs yourself; confirm the
   printed fractions and the seeded simulation numbers.
4. Solve EXERCISES.md before reading its solutions, then check.
5. Drill FLASHCARDS.md until the statement cards are verbatim.
