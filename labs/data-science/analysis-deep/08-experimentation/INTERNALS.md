# Internals - Experimentation Computations

## Normal CDF via erf

Abramowitz-Stegun 7.1.26 rational approximation, max error ~1.5e-7 -
five orders below any decision threshold used here. No lookup tables,
no dependencies, deterministic across JVMs.

## Chi-square 1-df closed form

For two arms the 1-df CDF equals erf(sqrt(chi2/2)) - exact, not an
approximation. k > 2 arms would need the incomplete gamma; out of
scope, documented at the call site.

## Power table

O(1) per n: one sqrt per row. Inputs are assumed planning rates, kept
in a separate type (PlanRate) from observed rates so planning numbers
can never leak into a readout.

## Overflow discipline

Counts are long; products like x*(n-x) cast to double before dividing.
n = 0 and x > n throw IllegalArgumentException with the offending arm
named - silent clamping is banned.

## Determinism

Zero randomness in analysis paths: same counts, same readout, every
JVM. The only RNG in the lab lives in the peeking exercise with a
fixed seed, and its seed is part of the printed output.

## Edge cases

- Zero conversions in both arms: d = 0, SE = 0, z = 0/0 - throw a named
  exception (no information) instead of printing NaN as a result.
- Tiny p (z > 8): erf saturates to exactly 0.0 in doubles - report p as
  "< 1e-15" style text rather than a false exact zero.
- Unbalanced arms (90/10 ramp): formulas hold as written; power follows
  the smaller arm, so size ramps by it.

## Why unpooled SE here

Unpooled SE matches the CI duality used throughout (interval excludes 0
iff p < 0.05). Pooled variants exist for the test-only view; mixing the
two definitions is the classic CI/p disagreement bug.
