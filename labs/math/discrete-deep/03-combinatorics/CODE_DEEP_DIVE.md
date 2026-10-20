# Code Deep Dive — Counted Three Ways, Every Time

Two runnable Python programs (stdlib only); every text block below is captured output.

## 1. Stars and Bars: Formula vs Brute Census

```python
from math import comb
from itertools import product

sols = lambda n, k, lo=0: [xs for xs in product(range(lo, n + 1), repeat=k)
                           if sum(xs) == n]
print("== stars and bars, xi >= 0 ==")
for (n, k) in [(10, 3), (6, 4), (5, 2), (12, 5)]:
    print("x1+..+x%d=%d: brute %d, closed C(%d,%d) = %d  match: %s" %
          (k, n, len(sols(n, k)), n + k - 1, k - 1, comb(n + k - 1, k - 1),
           len(sols(n, k)) == comb(n + k - 1, k - 1)))
print("== strictly positive x_i >= 1 ==")
for (n, k) in [(10, 3), (10, 4), (7, 2)]:
    print("x1+..+x%d=%d: brute %d, closed C(%d,%d) = %d  match: %s" %
          (k, n, len(sols(n, k, 1)), n - 1, k - 1, comb(n - 1, k - 1),
           len(sols(n, k, 1)) == comb(n - 1, k - 1)))
sample = sols(5, 2)
print("sample solutions of x1+x2=5:", sample[:4], " (total %d)" % len(sample))
```

Observed output:

```text
== stars and bars, xi >= 0 ==
x1+..+x3=10: brute 66, closed C(12,2) = 66  match: True
x1+..+x4=6: brute 84, closed C(9,3) = 84  match: True
x1+..+x2=5: brute 6, closed C(6,1) = 6  match: True
x1+..+x5=12: brute 1820, closed C(16,4) = 1820  match: True
== strictly positive x_i >= 1 ==
x1+..+x3=10: brute 36, closed C(9,2) = 36  match: True
x1+..+x4=10: brute 84, closed C(9,3) = 84  match: True
x1+..+x2=7: brute 6, closed C(6,1) = 6  match: True
sample solutions of x1+x2=5: [(0, 5), (1, 4), (2, 3), (3, 2)]  (total 6)
```

## 2. Bounds, Derangements, and the Thousand-Case Census

```python
from math import comb, factorial
from itertools import product, permutations

bounded = lambda n, hi, k: sum(1 for xs in product(range(hi + 1), repeat=k)
                               if sum(xs) == n)
n, hi, k = 10, 5, 3
bad1 = comb(n - (hi + 1) + k - 1, k - 1)
print("xi<=5 census x1+x2+x3=10: brute %d; I-E %d - 3*%d + 0 = %d" %
      (bounded(n, hi, k), comb(n + k - 1, k - 1), bad1,
       comb(n + k - 1, k - 1) - k * bad1))

derange = lambda n: sum((-1) ** m * comb(n, m) * factorial(n - m)
                        for m in range(n + 1))

for nn in (2, 3, 4, 5, 6):
    brute = sum(1 for p in permutations(range(nn))
                if all(p[i] != i for i in range(nn)))
    print("!%d: brute %d, formula %d" % (nn, brute, derange(nn)))

print("n=5 signed terms:", [((-1) ** m) * comb(5, m) * factorial(5 - m)
                            for m in range(6)], " sum:", derange(5))

f = [1000 // d for d in (2, 3, 5)]
p = [1000 // d for d in (6, 10, 15)]
union = sum(f) - sum(p) + 1000 // 30
print("I-E union divisible by 2, 3, or 5:", union)
surv = sum(1 for x in range(1, 1001) if x % 2 and x % 3 and x % 5)
print("survivors (no factor in {2,3,5}):", surv, "= 1000 -", union, ":", surv == 1000 - union)
print("floors 2,3,5 | 6,10,15 | 30:", f + p + [1000 // 30])
print("first survivors in 1..60:",
      [x for x in range(1, 61) if x % 2 and x % 3 and x % 5])
```

Observed output:

```text
xi<=5 census x1+x2+x3=10: brute 21; I-E 66 - 3*15 + 0 = 21
!2: brute 1, formula 1
!3: brute 2, formula 2
!4: brute 9, formula 9
!5: brute 44, formula 44
!6: brute 265, formula 265
n=5 signed terms: [120, -120, 60, -20, 5, -1]  sum: 44
I-E union divisible by 2, 3, or 5: 734
survivors (no factor in {2,3,5}): 266 = 1000 - 734 : True
floors 2,3,5 | 6,10,15 | 30: [500, 333, 200, 166, 100, 66, 33]
first survivors in 1..60: [1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 49, 53, 59]
```

Line-verified identity: union 734 and survivors 266 with
1000 − 734 = 266 printed equal True.
