# Numerical Methods - Math Foundation

Four sections derive the machinery in exact arithmetic; floats agree only after the algebra has spoken.

## 1. Bisection: The Interval Contract, in Exact Fractions

f(x) = x^3 - x - 2 has f(1) = -2 and f(2) = 4, so a sign change
brackets one root in [1, 2] (and f' = 3x^2 - 1 > 0 there, so it is
the only one). Bisection keeps the sign-changing half each step.
The exact ledger for the first four mids:

    k   mid     f(mid), exact                            kept
    1   3/2     27/8 - 3/2 - 2 = -1/8                    [3/2, 2]
    2   7/4     343/64 - 7/4 - 2 = 103/64                [3/2, 7/4]
    3   13/8    2197/512 - 13/8 - 2 = 341/512            [3/2, 13/8]
    4   25/16   15625/4096 - 25/16 - 2 = 1033/4096       [3/2, 25/16]

A positive mid moves the right bracket down; never up. After n
admissions the width is (b - a)/2^n, so the deep dive's ten steps
leave 2^-10 = 1/1024, error at most half of that: 1/2048 =
0.00048828125, printed 0.0004883. A promise about the interval,
not the achieved error.

## 2. Newton's Step From Taylor's Theorem

Write e = r - x. Taylor with remainder gives
0 = f(r) = f(x) + f'(x)e + f''(c)e^2/2 for some c near r, so
f(x) = f'(x)e + f''(c)e^2/2. One Newton step x+ = x - f(x)/f'(x)
therefore carries the new error
e+ = f''(c)e^2/(2f'(x+)): the old error squared, times a slowly
varying constant. For our cubic, f'' = 6x and f' = 3x^2 - 1, so the
forecast constant is 6r/(2(3r^2 - 1)) = 0.76788...(run:
0.7678837587311055); columns |e/e_prev^2| of 0.5019, 0.6816, 0.7593
climb toward it. The exact cross-check, entirely in fractions:

    f(2) = 4, f'(2) = 11  ->  x1 = 2 - 4/11 = 18/11
    f(18/11) = (5832-2178-2662)/1331 = 992/1331; f'(18/11) = (972-121)/121 = 851/121
    step = 992/9361; x2 = 18/11 - 992/9361 = (18*851 - 992)/9361 = 14326/9361

14326/9361 = 1.5303920521311825, and the float run printed
1.5303920521312: agreement through every shown place. The fraction
chain is the proof; the float trace is merely its witness.

## 3. Newton Can Fail: An Exact Cycle

f(x) = x^3 - 2x + 2 started from x0 = 0, in integers only:

    f(0) = 2, f'(0) = -2 -> x1 = 0 - 2/(-2) = 1; f(1) = 1, f'(1) = 1 -> x2 = 0

The map sends 0 to 1 and 1 to 0, so Newton orbits forever
(run: 1 -> 0 -> 1 -> 0 -> 1 -> 0 -> 1 -> 0). The tangent at 0 aims
at 1 and the tangent at 1 aims straight back: convergence is local,
guaranteed inside the basin, a cointoss outside, and the method
never announces which case you sit in.

## 4. Fixed Point Iteration and Its Speedometer

A map g with g(r) = r converges locally when |g'(r)| < 1, and then
error ratios drift to g'(r) (linear). For g(x) = exp(-x) the fixed
point r = 0.5671432904097839 has g'(r) = -exp(-r) = -r: signs must
alternate and magnitudes must shrink toward 0.567. Measured ratios
-0.4603, -0.6276, -0.5331, -0.5865 do exactly that. Newton on the
same equation f(x) = exp(-x) - x carries constant
f''(r)/(2f'(r)) = r/(2(1 + r)) = 0.1809..., and the run's
|e/e_prev^2| columns of 0.1562, 0.1826, 0.1810 confirm the forecast.
Score: four fixed point steps left 3.9e-2 of error; three Newton
steps left 4.4e-9.

Slope verdicts for two maps aiming at the r of x^3 - x - 2:

    g2(x) = 2/(x^2 - 1): at r, r^2 - 1 = 2/r, so |g2'(r)| = 4r*r^2/4
      = r^3 = 3.5214 > 1 -> diverges (run: |x - r| = 1.258e+00 after 12 iters)
    g3(x) = sqrt(1 + 2/x): |g3'(r)| = 1/(r^2 * r) = 1/r^3 = 0.2840 < 1
      -> converges (run: 9.594e-08 after 12 iters)

## 5. Quadrature: Trapezoid h^2, Simpson h^4, Edge Terms Decide

The sharp composite trapezoid error on [0, 1], via Euler-Maclaurin, is (f'(1) - f'(0))*h^2/12. Two forecasts, both checkable:

    e^x trapezoid forecast at n = 32: (e - 1)/12/32^2 = 1.398e-04 (run: 0.000139832)
    e^x Simpson sharp term (f'''(1) - f'''(0))*h^4/180 = (e - 1)/180/32^4 = 9.1e-09 (run: 0.000000009)

For f = 1/(1 + x^2): f'(x) = -2x/(1 + x^2)^2, so
f'(1) - f'(0) = -1/2 and the trapezoid forecast with h = 1/4 is
0.5/12/16 = 0.00260417 against the measured 0.002604046 - the
constant, not merely the order, was predicted in advance. This
integrand also kills Simpson's edge term, because
f'''(x) = 24x(1 - x^2)/(1 + x^2)^4 vanishes at both ends; the h^4
piece is exactly zero and the run's Simpson ratios leapt past 16 to
158.98 and 63.90, while e^x shows 15.91 -> 15.99. Same rules,
different constants, all derivable before any number is measured.

## 6. Doubles: 53 Bits, and What Cancellation Costs

A double carries a 53-bit significand; above 2^53 = 9007199254740992
integers lose unit spacing (the gap at 10^16 is 2), so 10^16 + 1
rounds back to 10^16 and the run's float subtraction printed 0.0
where the integer subtraction printed 1. In x^2 - Bx + C with
B = 1e8 the discriminant is harmless; the damage happens in
(B - sqrt(disc))/2, where two ~10^8 magnitudes nearly cancel and a
few ulps of error survive inside a ~1e-8 answer. Naive:
7.450580597e-09 against the true 1e-8, a 25.49% miss. Stable:
C/root_big = 1e-08, exactly.
