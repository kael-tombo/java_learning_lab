# Integration Techniques -- Math Foundation

All values computed in Python; observed outputs pasted. Every
antiderivative is verified by differentiating back.

## 1. Substitution: int 2x e^{x^2} dx

u = x^2, du = 2x dx: integral = int e^u du = e^u + C = e^{x^2} + C.
Differentiation-back at x = 0.7: analytic 2*0.7*e^{0.49} =
2.28524270793753 (observed); numeric central difference of e^{x^2}
with h = 1e-5: 2.2852427082331594 (observed). Agreement to 9 figures.
Definite check: int_0^1 2x e^{x^2} dx = e - 1 = 1.718281828459045
(observed).

## 2. Parts: int x e^x dx, Evaluated 0 to 2

u = x, dv = e^x dx: du = dx, v = e^x. int x e^x dx = x e^x - e^x + C
= (x-1)e^x + C. Back-check: d/dx [(x-1)e^x] = e^x + (x-1)e^x = x e^x.
Definite 0 to 1: [(x-1)e^x]_0^1 = 0 - (-1) = 1. Definite 0 to 2:
[(x-1)e^x]_0^2 = e^2 - (-1) = e^2 + 1 = 8.38905609893065 (observed).

## 3. Partial Fractions: int_0^1 dx/((x+1)(x+2))

Split: 1/((x+1)(x+2)) = 1/(x+1) - 1/(x+2). Integral: ln(x+1) -
ln(x+2) evaluated 0 to 1 = (ln 2 - ln 3) - (ln 1 - ln 2) = 2 ln 2 -
ln 3 = 0.2876820724517808 (observed). Back-check of the split at
x = 0.5: 1/(1.5*2.5) = 0.26666..., and 1/1.5 - 1/2.5 = 0.66666...
- 0.4 = 0.26666... (observed 0.26666666666666666 vs 0.2666666666666666,
agreeing to 16 figures).

## 4. Trig Power: int sin^2 x dx

sin^2 x = (1 - cos 2x)/2, so the antiderivative is x/2 - sin(2x)/4
+ C. Back-check: d/dx [x/2 - sin(2x)/4] = 1/2 - cos(2x)/2 = sin^2 x
by the double-angle identity. Definite 0 to pi: [x/2 - sin(2x)/4]_0^pi
= pi/2 - 0 = 1.5707963267948966 (observed). Average of sin^2 over a
period is 1/2, and pi * 1/2 = pi/2 confirms the same value.

## 5. Arctan Integral: int_0^1 dx/(1+x^2)

Antiderivative arctan x (check: d/dx arctan x = 1/(1+x^2)). Value:
arctan 1 - arctan 0 = pi/4 = 0.7853981633974483 (observed). Midpoint
rule with n = 1000 gives 0.7853981842307817 (observed), within
2.1e-8 of pi/4 -- the closed form and the numeric sum agree.
