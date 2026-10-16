# Limits and Continuity -- Math Foundation

Every value below was computed in Python (float spot-checks plus exact
rational steps) and the observed outputs are pasted in, not hand-derived.

## 1. Removable Discontinuity by Factoring

lim_{x -> 2} (x^2 - 4)/(x - 2). For x != 2, factor: (x-2)(x+2)/(x-2)
= x + 2, so the limit is 4 by direct substitution into x + 2.
Spot-check: at x = 1.5 the expression evaluates to 3.5 = 1.5 + 2
(observed), on the line y = x + 2 approaching 4. The function is still
undefined at x = 2; setting f(2) = 4 removes the discontinuity.

## 2. Rationalization

lim_{x -> 4} (sqrt(x+5) - 3)/(x - 4). Multiply by the conjugate:
(sqrt(x+5)-3)(sqrt(x+5)+3) / ((x-4)(sqrt(x+5)+3)) = (x - 4)/((x-4)
(sqrt(x+5)+3)) = 1/(sqrt(x+5) + 3) for x != 4. Substitute x = 4:
1/6 = 0.16666666666666666. Numeric approach (observed):
x = 4.001 -> 0.16666203729437376; x = 4.0001 -> 0.1666662037051457;
x = 3.9999 -> 0.16666712963040808. Both sides converge to 1/6.

## 3. Special Trigonometric Limits

lim_{x -> 0} sin(3x)/x = 3 lim_{u -> 0} sin(u)/u with u = 3x, and
lim sin(u)/u = 1, so the limit is 3. Observed at x = 0.0001:
2.9999999550000003. Next, (1 - cos x)/x^2: multiply by (1 + cos x):
(1 - cos^2 x)/(x^2 (1 + cos x)) = (sin x / x)^2 / (1 + cos x) -> 1/2.
Observed at x = 0.001: 0.49999995832550326 against 1/2.

## 4. L'Hopital's Rule (Conditions Checked)

lim_{x -> 0} (e^x - 1 - x)/x^2 is 0/0 with numerator and denominator
differentiable near 0 and denominator nonzero nearby, so L'Hopital
applies: first derivatives give (e^x - 1)/(2x), still 0/0, so apply
again: e^x/2 -> 1/2. Observed at x = 0.001: 0.5001667083845766,
within O(x) = 0.001 of 1/2 as the Taylor remainder predicts
(e^x = 1 + x + x^2/2 + x^3/6 + ...).

## 5. Squeeze Example, Fully Bounded

For x != 0, -|x| <= x sin(1/x) <= |x| since |sin| <= 1. Both bounds
tend to 0, so lim_{x -> 0} x sin(1/x) = 0. Observed: at x = 0.001 the
value is 0.001 sin(1000) with |value| <= 0.001, pinned by the bounds.
The oscillation never matters because the envelope |x| crushes it.
