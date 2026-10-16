# Derivative Applications

## Overview

What derivatives are for: locating and classifying extrema (Fermat,
first/second derivative tests, EVT on closed intervals), solving
optimization models end to end, differentiating implicit time
relations (related rates), and linear approximation with a Lagrange
error bound.

## Contents

- THEORY.md: critical points, both derivative tests with their
  inconclusive cases, EVT hypotheses, optimization protocol, related
  rates, linear approximation and differentials.
- MATH_FOUNDATION.md: cubic x^3-3x^2-9x+5 classified (max 10 at -1,
  min -22 at 3); 12x12 open box maximized (x=2, V=128, EVT table);
  sphere dV/dt = 200 pi = 628.3185307179587; sqrt(26) ~= 5.1 with
  error 0.00098 inside the 0.001 bound.
- CODE_DEEP_DIVE.md: sign-chart probes, volume scan, rate evaluation,
  approximation error -- all executed.

## Prerequisites

Derivative rules (lab 02); EVT needs continuity (lab 01).

## How to work this lab
Classify every critical point with a sign chart before trusting the
second-derivative test — the inconclusive case (f'' = 0) appears in the
exercises deliberately. For optimization, write the EVT table (endpoints
plus critical points) in full; skipping the table is how maxima escape.
Check the related-rates units at each step: dV/dt in volume-per-time
catches most setup errors.
