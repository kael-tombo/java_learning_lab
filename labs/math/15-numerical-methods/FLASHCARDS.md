# Numerical Methods - Flashcards, Run-Backed

Twelve cards; every figure is a captured output or an exact
derivation the runs confirm.

### Card M1
**Prompt:** Bisection's guarantee after n halvings of a bracketing interval.
**Reply:** Error at most width/2^n. For x^3 - x - 2 on [1, 2] ten
steps leave width 2^-10, and the run printed bound |b - a|/2 =
0.0004883, which is exactly 1/2048. A bound is a promise, not a
measurement.

### Card M2
**Prompt:** The exact f-values behind the first four bisection midpoints.
**Reply:** f(3/2) = -1/8, f(7/4) = 103/64, f(13/8) = 341/512,
f(25/16) = 1033/4096. The float column printed -0.125000, +1.609375,
+0.666016, +0.252197: roundings of these very fractions.

### Card M3
**Prompt:** Where Newton's quadratic rate constant comes from.
**Reply:** Dividing e by e_prev^2 tends to f''(r)/(2f'(r)). For
x^3 - x - 2 that is 6r/(2(3r^2 - 1)) = 0.76788... (run printed
0.7678837587311055), and the columns 0.5019, 0.6816, 0.7593 climb
toward it.

### Card M4
**Prompt:** Newton's first two iterates from x0 = 2 on x^3 - x - 2, exactly.
**Reply:** x1 = 2 - 4/11 = 18/11 (float print 1.6363636363636);
x2 = 18/11 - 992/9361 = 14326/9361 = 1.5303920521311825 (float
print 1.5303920521312).

### Card M5
**Prompt:** How x^3 - 2x + 2 defeats Newton started at x0 = 0.
**Reply:** In integers: f(0) = 2, f'(0) = -2 gives x1 = 1; f(1) = 1,
f'(1) = 1 gives x2 = 0. The run looped
1 -> 0 -> 1 -> 0 -> 1 -> 0 -> 1 -> 0 forever, no floating point
needed to see it.

### Card M6
**Prompt:** The fixed point of x <- exp(-x) and the iteration's measured temper.
**Reply:** r = 0.5671432904097839. Ratios e/e_prev printed -0.4603,
-0.6276, -0.5331, -0.5865: alternating sign, magnitudes sliding
toward g'(r) = -exp(-r) = -r. Linear, slow, locally sure.

### Card M7
**Prompt:** Newton's version of the same race, and its speedometer.
**Reply:** From x0 = 1 on f(x) = exp(-x) - x, three steps landed
4.4e-9 from r; |e/e_prev^2| columns 0.1562, 0.1826, 0.1810 match the
forecast r/(2(1 + r)) = 0.1809. Plain fixed point needed four steps
merely to reach 3.9e-2.

### Card M8
**Prompt:** Two maps for the cubic's root, one converging and one not.
**Reply:** g2(x) = 2/(x^2 - 1): |g2'(r)| = r^3 = 3.5214, divergent
(run: |x - r| = 1.258e+00 after 12 iters). g3(x) = sqrt(1 + 2/x):
|g3'(r)| = 1/r^3 = 0.2840, convergent (run: 9.594e-08 after 12
iters).

### Card M9
**Prompt:** The halving signature of each quadrature rule on e^x.
**Reply:** Trapezoid error divided by 4.00, 4.00, 4.00 (order h^2);
Simpson's by 15.91, 15.98, 15.99 (order h^4, ratio settling to 16).

### Card M10
**Prompt:** Trapezoid and Simpson error forecasts on [0, 1] at n = 32 for e^x.
**Reply:** (e - 1)h^2/12 = 1.398e-04 next to the measured
0.000139832; (e - 1)h^4/180 = 9.1e-09 next to the measured
0.000000009. Prediction and measurement agree to 3-4 digits.

### Card M11
**Prompt:** Why Simpson's ratios on the pi/4 integrand leapt past 16.
**Reply:** f'''(x) = 24x(1 - x^2)/(1 + x^2)^4 vanishes at both
ends, so the sharp (f'''(1) - f'''(0))*h^4/180 term is exactly 0
there; with the h^4 piece dead the run printed 158.98 and 63.90. A
zero edge term, not magic.

### Card M12
**Prompt:** The two cancellation exhibits from the integers-versus-floats run.
**Reply:** (10^16 + 1) - 10^16 is 1 in integers, 0.0 in doubles
(53-bit significand; the gap at 10^16 is 2). And the naive small
root of x^2 - 1e8*x + 1 printed 7.450580597e-09, 25.49% off the
true 1e-8, while C/root_big printed 1e-08.
