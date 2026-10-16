# Integration Techniques

## Overview

The working toolkit: substitution (inverted chain rule), parts
(inverted product rule), partial fractions, trig integrals and trig
substitution, and improper integrals with the p-test. Every
antiderivative is checked by differentiating back, and every definite
value is confirmed numerically.

## Contents

- THEORY.md: substitution, parts with LIATE, partial fractions,
  trig reduction and the three trig substitutions, improper
  integrals and convergence (p-test).
- MATH_FOUNDATION.md: five worked integrals -- 2x e^{x^2} to e-1 on
  [0,1]; x e^x to e^2+1 = 8.38905609893065 on [0,2]; partial
  fractions to 2 ln 2 - ln 3 = 0.2876820724517808; sin^2 to pi/2 on
  [0,pi]; 1/(1+x^2) to pi/4 = 0.7853981633974483.
- CODE_DEEP_DIVE.md: differentiation-back harness, midpoint
  confirmation of pi/4, split-identity check.

## Prerequisites

Integral fundamentals (lab 04); chain/product rules (lab 02).

## How to work this lab
Choose the technique before computing: substitution needs a visible
inner derivative, parts needs LIATE ordering, partial fractions need a
factored denominator. Then differentiate your answer back — the harness
does this automatically, and a mismatch always means an algebra slip
(constant factors, chain leftovers) rather than a method error.
