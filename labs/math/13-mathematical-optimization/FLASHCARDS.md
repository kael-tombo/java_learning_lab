# Optimization — Flashcards, Run-Backed

Twelve cards; every number is a run value or an exact hand check
cross-confirmed in one.

### Card O1
**Q:** One factor to rule all four destinies of GD on x².
**A:** (1 − 2η). Run values: 3/5 and 1/5 converge; −1/10 oscillates
sharply (5 → −1/2 → 1/20 → ...); −1 orbits 5, −5, 5 forever;
−11/10 diverges: −11/2 → 121/20 → −1331/200 → ...

### Card O2
**Q:** On x², where exactly does gradient descent stop converging?
**A:** The driver is |1 − 2η| against 1. η = 1 makes the factor −1:
an eternal orbit, verified by the run printing 5 → −5 → 5 → −5 —
while η = 1/2 annihilates in one step (factor 0). Both boundaries
are exact because |1 − 2η| hits 1 at η = 1; past it (η = 21/20,
factor −11/10) the run diverges.

### Card O3
**Q:** Two curvature directions, one scalar rate — what goes wrong?
**A:** x² + 10y² has direction factors (1 − 2η) and (1 − 20η). At
η = 9/100: x shrinks by 41/50 each step while y bounces by −4/5 —
the run's y chain 1 → −4/5 → 16/25 → −64/125 is the zigzag in
fractions.

### Card O4
**Q:** Where is the zigzag sharpest and slowest compromise?
**A:** η = 3/40 printed x factor 17/20 (5 → 17/4 → 289/80) and y
factor −1/2 (1 → −1/2 → 1/4). The y-chain halves in magnitude and
flips sign every step, while x grinds at 0.85 per step.

### Card O5
**Q:** The convexity test sequence for f = x² + 6xy + y², and its verdict.
**A:** H = [[2, 6], [6, 2]]: leading minors 2 and −32 → indefinite →
NOT convex, despite resembling a bowl. Runs printed eigenvalues 8
and −4 from λ² − 4λ − 32 = 0, and the decomposition
f = (x + 3y)² − 8y² exposes the two-sidedness.

### Card O6
**Q:** Which quadratics passed convexity in the run?
**A:** x² + y² (minors 2, 4) and x² + 4y² (minors 2, 16) — positive
definite, strictly convex. x² − y² (2, −4) and xy (0, −1) failed as
expected saddles; the 6xy-mixed form failed too.

### Card O7
**Q:** The five LP vertices and their z = 2x + 3y scorecard.
**A:** Infeasible pairs: (0, 4) and (6, 0). Feasible: (0, 0) → 0,
(4, 0) → 8, (0, 2) → 6, and the interior intersection (3, 1) → 9,
which was the optimum. Enumeration replaced cleverness.

### Card O8
**Q:** Why does the (3, 1) vertex beat the corner (4, 0) for one goal but not another?
**A:** max 3x + 2y picks (4, 0) with z = 12 over (3, 1) with 11
(run-printed); max 2x + 3y picks (3, 1) with z = 9 over (4, 0)
with 8. The objective's weights arbitrate among feasible vertices —
the feasible set stays fixed.

### Card O9
**Q:** Exact critical values of the tilted quartic f = x⁴/4 − 2x² + x/4.
**A:** f(−2) = −9/2 and f(2) = −7/2, printed by the run: the +x/4
tilt breaks the symmetric quartic's tie, making the LEFT minimum
global and the right one merely local.

### Card O10
**Q:** What did the five quartic starts actually resolve to?
**A:** −3, −1, 0 all landed at x = −2.0305 with f = −4.5038;
1/5 and 3 landed at x = 1.9680 with f = −3.5040. Endpoints differ
by ~1.0 — a basin verdict, not noise. The exact first step from
−1 printed as x₁ = −53/40.

### Card O11
**Q:** Does "gradient zero" imply "minimum"? Exhibit the counterexample exactly.
**A:** No — on the untilted symmetric quartic x⁴/4 − 2x², f'(0) = 0
but f(0) = 0 while f(±1) = 1/4 − 2 = −7/4 (exact), so 0 is a LOCAL
MAX that GD halts at if it starts there. The tilted lab version
escapes this only because its f'(0) = 1/4 ≠ 0.

### Card O12
**Q:** Quick exact sanity check on descent's first step from −1 on the quartic.
**A:** f'(−1) = −1 + 4 + 1/4 = 13/4; x₁ = −1 − (1/10)(13/4) = −53/40,
printed by the run. One fraction, one verification — the exactness
charge scales to every later step.
