# MINI_PROJECT — Limits & Continuity: Numerical Limit Explorer
> Implement + tabulate + verify. ~2 hours.

## Goal
Build a CLI that numerically approaches limits from both sides, flags discontinuities,
verifies the IVT on scanned intervals, and cross-checks against analytic answers.

## Build Steps
1. `Limit.java`: f evaluated at a±10⁻ᵏ for k=1..6; both-side match test.
2. `Continuity.java`: sample a function, detect jumps/infinities.
3. `IVT.java`: scan [a,b]; report sign-change subintervals.
4. Driver: table for (x²−4)/(x−2), 1/x, sin(x)/x; print verdicts.

## Acceptance
- [ ] One-sided mismatch flagged for 1/x at 0.
- [ ] IVT finds an interval for x³−x−2.
- [ ] Numerical limit within 1e-4 of analytic.

## Extensions
- Richardson extrapolation on the limit table.
