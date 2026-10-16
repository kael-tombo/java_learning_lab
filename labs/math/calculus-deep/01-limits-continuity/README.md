# Limits and Continuity

## Overview

Limits make "arbitrarily close" precise via epsilon-delta; continuity
means the limit equals the function value. This lab covers one- and
two-sided limits, limit laws, factoring, rationalization, the squeeze
theorem, L'Hopital's rule with its hypotheses, discontinuity types,
and the Intermediate Value Theorem.

## Contents

- THEORY.md: epsilon-delta, limit laws, continuity, squeeze, IVT,
  removable/jump/infinite discontinuities.
- MATH_FOUNDATION.md: five worked limits with every step shown --
  factoring to 4, rationalization to 1/6, sin(3x)/x to 3,
  (1 - cos x)/x^2 to 1/2, L'Hopital to 1/2, squeeze to 0 --
  each with executed numeric confirmation.
- CODE_DEEP_DIVE.md: stdlib-only Python snippets that approach each
  limit from both sides; outputs embedded.

## Key Results

| Limit | Value | Verified at |
|---|---|---|
| (x^2-4)/(x-2), x->2 | 4 | x=1.5 gives 3.5 |
| (sqrt(x+5)-3)/(x-4), x->4 | 1/6 | x=4.0001 gives 0.16666620... |
| sin(3x)/x, x->0 | 3 | x=1e-4 gives 2.999999955 |
| (1-cos x)/x^2, x->0 | 1/2 | x=1e-3 gives 0.4999999583 |

## Prerequisites

Algebra (factoring, conjugates), function notation, basic trig.
