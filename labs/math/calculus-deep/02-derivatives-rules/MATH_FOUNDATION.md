# Derivatives and Rules -- Math Foundation

All derivatives below were differentiated by hand from the rules and
then confirmed by central differences (h = 1e-5); observed values pasted.

## 1. Product Rule: d/dx [x^2 e^x] at x = 2

f' = 2x e^x + x^2 e^x = e^x (2x + x^2). At x = 2: e^2 * 8 =
59.1124487914452 (observed via math.exp). Central difference with
h = 1e-5: 59.112448794529364 (observed) -- agreement to 8 significant
figures, confirming the rule application.

## 2. Chain Rule: d/dx [ln(x^2 + 1)] at x = 2

Outer ln(u), u = x^2+1: f' = (1/u)(2x) = 2x/(x^2+1). At x = 2: 4/5
= 0.8 exactly. Central difference (observed): 0.8000000000008.
Common error this catches: forgetting the inner 2x gives 1/5 = 0.2,
which the numeric check refutes.

## 3. Quotient Rule: d/dx [(x^3 + 1)/(x - 1)] at x = 2

f' = (3x^2 (x-1) - (x^3+1)(1))/(x-1)^2. At x = 2: numerator
3*4*1 - 9 = 12 - 9 = 3, denominator 1, so f'(2) = 3. Central
difference (observed): 2.9999999998864264. Note the function value
f(2) = 9, so the tangent line at x = 2 is y = 9 + 3(x - 2).

## 4. Chain + Trig: d/dx [sin^2(3x)] at x = 0.5

Write sin^2(3x) = (sin 3x)^2. Outer power, middle sin, inner 3x:
f' = 2 sin(3x) cos(3x) * 3 = 3 sin(6x). At x = 0.5: 3 sin(3) =
0.4233600241796016 (observed). Central difference (observed):
0.42336002392673316 (agreement to 9 figures). The double-angle form
3 sin(6x) is exact, not an approximation.

## 5. MVT Check on f(x) = x^2, [1, 3]

Secant slope: (9 - 1)/(3 - 1) = 4. MVT promises c with f'(c) = 2c
= 4, i.e. c = 2, interior to (1, 3). Verified directly: f'(2) = 4.
Second check on f(x) = x^3, [0, 2]: secant slope (8 - 0)/2 = 4,
f'(c) = 3c^2 = 4 gives c = 2/sqrt(3) = 1.1547005383792517 (observed),
interior to (0, 2). Both cases exhibit the promised interior point.
This is the theorem holding with equality exhibited on a case whose
c is computable in closed form.
