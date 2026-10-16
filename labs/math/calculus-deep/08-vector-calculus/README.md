# Vector Calculus

## Overview

Fields in three dimensions: gradient, divergence, and curl evaluated
at points (div 12, curl (0,0,0) for (x^2,y^2,z^2); curl (0,0,2) for
(-y,x,0)), conservative fields with potentials verified on two paths,
a line integral worked to 1 with its Riemann confirmation, and Green
(2 pi both sides) plus divergence-theorem flux (4 pi both sides).

## Contents

- THEORY.md: grad/div/curl definitions, conservative-field criterion,
  line and surface integrals, Green/Stokes/divergence theorems with
  exact hypotheses, a guide to which theorem applies.
- MATH_FOUNDATION.md: div/curl at (1,2,3); line integral along
  (t,t^2) equal to 1; potential x^2+y^2 giving 2 on two paths; Green
  2 pi = 2 pi; flux 4 pi = 4 pi.
- CODE_DEEP_DIVE.md: component checks, midpoint line-integral sum
  0.9999999999750026, Green/Gauss spot values, path-independence
  equality 2 = 2.0.

## Prerequisites

Multivariable calculus (lab 07); single-variable integrals (lab 04).

## How to work this lab
Decide the theorem before computing: closed curve in the plane means
Green, closed surface means divergence, conservative field means find
the potential and evaluate endpoints. Verify curl/divergence components
individually first — a single wrong partial invalidates the whole
integral, and component checks isolate it in seconds.
