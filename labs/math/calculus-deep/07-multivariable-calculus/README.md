# Multivariable Calculus

## Overview

Calculus in two variables: partials with Clairaut, gradient and
directional derivatives, tangent planes, the Hessian second-derivative
test, and iterated integrals via Fubini. Worked around f(x,y) =
x^2 y + 3x y^2 at (2,1) -- grad (7,16), directional 17 -- and
g(x,y) = x^2+y^2-4x-2y+5 with minimum 0 at (2,1).

## Contents

- THEORY.md: partials, gradient, tangent plane, critical-point test,
  chain rule, Fubini with a both-orders example (4 = 4).
- MATH_FOUNDATION.md: term-by-term partials, |grad| =
  17.46424919657298, plane error 0.004514, sum-of-squares minimum,
  iterated integrals both orders equal 4.
- CODE_DEEP_DIVE.md: gradient evaluation, plane-vs-true comparison,
  central-difference confirmation of fx, grid minimum, double Riemann
  sum tending to 4.

## Prerequisites

Single-variable derivatives and integrals (labs 02-04).

## How to work this lab
Compute partials term by term, then confirm fx against a central
difference before trusting the gradient — one sign error poisons every
downstream number (directional derivative, plane, optimum). For double
integrals, evaluate both orders; Fubini says they agree, and disagreement
locates the setup mistake to a specific limit.
