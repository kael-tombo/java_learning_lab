# Differential Equations

## Overview

First-order ODEs solved three ways -- separable, linear via
integrating factor, exponential growth -- each solution verified by
substitution with zero residual, plus Euler approximation with its
measured error and a logistic stability sketch.

## Contents

- THEORY.md: solution meaning, existence-uniqueness hypotheses,
  separable and linear methods, equilibria and stability, Euler error.
- MATH_FOUNDATION.md: y = 3e^{2t} (y(1) = 22.16716829679195);
  y = sqrt(x^2+4) with residual 0.0; y = 3 - 2e^{-2x} with residual
  0.0 and y(1) = 2.7293294335267744; Euler 2.5937424601 vs e;
  logistic equilibria 0 (unstable) and 10 (stable).
- CODE_DEEP_DIVE.md: residual harness, Euler loop equal to (1.1)^10,
  logistic iteration.

## Prerequisites

Derivatives (lab 02), integrals and FTC (lab 04), parts (lab 05).

## How to work this lab
Substitute every claimed solution back into the ODE and check the
residual is exactly zero before moving on — the harness asserts this,
and hand work should too. For Euler steps, halve the step and confirm
the error roughly halves (first-order behavior); if it does not, the
step loop (not the theory) has the bug.
