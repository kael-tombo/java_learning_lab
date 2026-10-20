# Lab 05 — Law of Large Numbers

Explains why averaged data earn trust, with the exact statement clams
(WLLN, SLLN, Borel–Cantelli) and executed demonstrations of bounds,
clocks, and hypothesis failure.

## What This Lab Actually Teaches
- Convergence in probability and why it is the honest notion for
  sample-path averages (THEORY.md).
- Markov and Chebyshev inequalities with exact statements.
- The weak law with its variance hypothesis and the
  P( deviation >= ε ) <= σ²/(nε²) proof skeleton.
- Borel–Cantelli as the summability-to-finite-violations converter.
- Kolmogorov's strong law with only the integrability hypothesis —
  and why that hypothesis is sharp.
- The CLT's σ/√n rate as the fluctuation scale of the mean.

## The Worked Material
MATH_FOUNDATION.md executes the 1/(4n) variance clock (1/16 at n = 4
down to 1/1024 at n = 256), the exact-vs-bound pair (1/8 truth under a
1/4 envelope), the vacuous-case check (bound 1/9 over event size 0),
a seeded four-row simulation to 10^6 draws with |dev| = 0.000447, the
heavy-tail crawl on weights (45, 30, 20, 5)% with 10^6 magnitudes, and
Tail-bound truths: e^{−3} = 0.049787068367863944 under 1/3 and 1/4
envelopes. CODE_DEEP_DIVE.md pastes the captured outputs.

## Files (core six)
| File | Contents |
|------|----------|
| THEORY.md | Statements: inequalities, WLLN, Borel–Cantelli, SLLN, CLT |
| MATH_FOUNDATION.md | Executed clock, bounds, simulation, heavy tails |
| CODE_DEEP_DIVE.md | Three seeded programs, outputs as printed |
| EXERCISES.md | Five problems, computed solutions |
| FLASHCARDS.md | 11 cards, six of them theorem-statement cards |
| README.md | This overview |

The other files in the directory (QUIZ code sources, projects,
HISTORY, and companions) remain untouched.

## Suggested Sequence
1. THEORY.md statements first — hypothesis lists matter more than
   conclusions here.
2. MATH_FOUNDATION.md against a fractions-enabled session.
3. Run the three programs; confirm digits reproduce.
4. EXERCISES.md attempts, then solutions.
5. FLASHCARDS.md — recite the two law statements and the two inequalities.
