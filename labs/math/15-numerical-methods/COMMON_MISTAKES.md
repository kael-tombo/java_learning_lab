# Common Mistakes - Numerical Methods

## 1. Reading the Bisection Bound as the Error Itself
The printed 0.0004883 is the largest possible error, half the kept
width. The true error can be far smaller or within a rounding step
of the bound. Report "at most", and say which quantity (half the
last width) the number actually is.

## 2. Trusting One Good-Looking Newton Iterate
x1 = 18/11 = 1.636... sits a visible distance from 1.5214, yet an
untimely iterate can look close by accident. What certifies the
quadratic regime is the behavior of |e/e_prev^2|
(0.5019 -> 0.6816 -> 0.7593, homing on 0.7679), not any single x on
the way.

## 3. Assuming Convergence Is Automatic
Two exhibits from the runs: x^3 - 2x + 2 orbits 1 -> 0 -> 1 -> 0
forever from x0 = 0 (proved first in integers), and the arctan
update from x0 = 2 sprinted -3.5357, 13.9510, -279.3441,
122016.9989. Neither failure announces itself; cap the iterations
and watch the size of each correction.

## 4. Forcing Big Integers Through Doubles
(10^16 + 1) - 10^16 equals 1 to integers and 0.0 to doubles: the
53-bit significand cannot hold the unit at scale 10^16, where the
gap is already 2. Keep integer quantities as integers, and let
floats in only when the value's size and the exponent both fit.

## 5. Forming Small Roots by Subtracting Nearly Equal Numbers
(B - sqrt(disc))/2 with B = 1e8 printed 7.450580597e-09, a 25.49%
miss on the true 1e-8: the subtraction deletes exactly the leading
digits the answer needs. The conjugate form small root = C/big_root
printed 1e-08 for the same input, no subtraction of giants.

## 6. Quoting h^2 and h^4 Without Their Edge Constants
"Trapezoid h^2, Simpson h^4" headlines the order, not the price.
The e^x run hides nothing: (e - 1)h^2/12 = 1.398e-04 matched the
measured 0.000139832 only because the sharp constant
(f'(1) - f'(0))/12 was used. Flip the integrand to 1/(1 + x^2) and
Simpson's h^4 term dies exactly (f'''(0) = f'''(1) = 0), sending
the ratios to 158.98 and 63.90; quoting 16 there would be a false
prediction.

## 7. Judging an Iteration by Looks Instead of Its Ratio
The fixed point walk x <- exp(-x) bounces
(+1.251e-01 then -6.667e-02 in the error) and can look unstable;
the ratio column says otherwise, sliding to -0.567. Conversely a
well-behaved-looking crawl can be linear with rate 0.9. The
speedometer is the error ratio (for Newton, e over e_prev^2), and
it is the only eyewitness worth obeying.
