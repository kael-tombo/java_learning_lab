# Code Deep Dive — Coefficients, Extracted and Cross-Checked

Two runnable Python programs (stdlib only); the output fences are literal captures.

## 1. Exact Polynomial Multiplication and the x = 1 Ledger

```python
def poly_mul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            r[i + j] += ai * bj
    return r

step = [1, 1]; base = [1, 1]
for _ in range(3):
    step = poly_mul(step, base)
print("(1+x)^4 coefficients:", step, " sum:", sum(step))
p = [1]; tri = [1, 1, 1]
for _ in range(3):
    p = poly_mul(p, tri)
print("(1+x+x^2)^3 coefficients:", p, " sum:", sum(p), " = 3^3 =", 3 ** 3)
lhs = sum(poly_mul([1, 1], [1, 1, 1]))
print("sum of coefficients of (1+x)(1+x+x^2):", lhs, " = 2 * 3 =", 2 * 3)
```

Observed output:

```text
(1+x)^4 coefficients: [1, 4, 6, 4, 1]  sum: 16
(1+x+x^2)^3 coefficients: [1, 3, 6, 7, 6, 3, 1]  sum: 27  = 3^3 = 27
sum of coefficients of (1+x)(1+x+x^2): 6  = 2 * 3 = 6
```

## 2. Product Semantics: Dice, Coins, Partitions, Euler's Collapse

```python
def poly_mul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            r[i + j] += ai * bj
    return r

die = [0, 1, 1, 1, 1, 1, 1]
d2 = poly_mul(die, die)
print("two-dice totals 2..12:", d2[2:])
print("sum of counts:", sum(d2), " ways total 7:", d2[7], " total 2:", d2[2])

dp = [0] * 11; dp[0] = 1
for c in (1, 2, 5):
    for i in range(c, 11):
        dp[i] += dp[i - c]
print("coin {1,2,5} ways 0..10:", dp, " exactly 10:", dp[10])
manual = [(a, b, c) for a in range(11) for b in range(6) for c in range(3) if a + 2 * b + 5 * c == 10]
print("brute triples:", manual)

p = [1] + [0] * 12
for k in range(1, 13):
    for i in range(k, 13):
        p[i] += p[i - k]
print("p(0..12):", p)

def parts_brute(n, k=None):
    k = n if k is None else k
    return 1 if n == 0 else (0 if k == 0 else
           sum(parts_brute(n - j * k, k - 1) for j in range(n // k + 1)))

print("brute p(10):", parts_brute(10), " p(12):", parts_brute(12))

def count(n, ks, downturn):
    dp = [0] * (n + 1); dp[0] = 1
    for k in ks:
        rng = range(n, k - 1, -1) if downturn else range(k, n + 1)
        for i in rng:
            dp[i] += dp[i - k]
    return dp[n]

print("distinct vs odd n=6..10:",
      [(m, count(m, range(1, m + 1), True), count(m, range(1, m + 1, 2), False),
        count(m, range(1, m + 1), True) == count(m, range(1, m + 1, 2), False))
       for m in range(6, 11)])
```

Observed output:

```text
two-dice totals 2..12: [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
sum of counts: 36  ways total 7: 6  total 2: 1
coin {1,2,5} ways 0..10: [1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 10]  exactly 10: 10
brute triples: [(0, 0, 2), (0, 5, 0), (1, 2, 1), (2, 4, 0), (3, 1, 1), (4, 3, 0), (5, 0, 1), (6, 2, 0), (8, 1, 0), (10, 0, 0)]
p(0..12): [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77]
brute p(10): 42  p(12): 77
distinct vs odd n=6..10: [(6, 4, 4, True), (7, 5, 5, True), (8, 6, 6, True), (9, 8, 8, True), (10, 10, 10, True)]
```

(One helper with the inner loop direction swapped gives the distinct-parts
product descending and the odd-parts product ascending — True on all five rows.)
