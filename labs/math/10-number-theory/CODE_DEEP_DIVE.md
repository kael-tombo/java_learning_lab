# Code Deep Dive — Number Theory, Run Certificate by Certificate

Three stdlib-only Python programs; every output block below is a
verbatim captured run.

## 1. Extended Euclid Emits Its Own Bezout Certificate

```python
def ext_gcd(a, b, trace=True):
    r0, r1, s0, s1, t0, t1 = a, b, 1, 0, 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1
        if trace:
            print("q=%d: %d*(%d) + %d*(%d) = %d" % (q, s1, a, t1, b, r1))
    return r0, s0, t0

g, x, y = ext_gcd(240, 46)
print("gcd(240, 46) = %d  via  %d*240 + %d*46" % (g, x, y))
_, u, v = ext_gcd(26, 7, trace=False)
print("inverse of 7 mod 26: %d | 7*%d mod 26 = %d" % (v % 26, v % 26, 7 * (v % 26) % 26))
g2, x2, y2 = ext_gcd(14, 6, trace=False)
print("6 mod 14: gcd = %d with %d*14 + %d*6 = %d, so no inverse exists" % (g2, x2, y2, g2))
```

Observed output:

```text
q=5: 1*(240) + -5*(46) = 10
q=4: -4*(240) + 21*(46) = 6
q=1: 5*(240) + -26*(46) = 4
q=1: -9*(240) + 47*(46) = 2
q=2: 23*(240) + -120*(46) = 0
gcd(240, 46) = 2  via  -9*240 + 47*46
inverse of 7 mod 26: 15 | 7*15 mod 26 = 1
6 mod 14: gcd = 2 with 1*14 + -2*6 = 2, so no inverse exists
```

The invariant s·a + t·b = r is renewed at every line, so the final
remainder arrives with its coefficients already attached; taking v
(the slot on 7) modulo 26 is the inverse, and the (14, 6) row shows
gcd 2 ≠ 1 blocking the inverse outright.

## 2. CRT as Four Small Numbers and One Sweep

```python
system = [(2, 3), (3, 5), (2, 7)]
M = 3 * 5 * 7
print("M =", M)
total = 0
for a, m in system:
    Mi = M // m
    yi = pow(Mi, -1, m)
    print("a=%d, m=%d: M/m = %d, inverse mod m = %d, piece = %d" % (a, m, Mi, yi, a * Mi * yi))
    total += a * Mi * yi
x = total % M
print("pieces sum to %d -> x = %d (mod %d)" % (total, x, M))
print("check x mod (3,5,7) =", [x % m for _, m in system])
print("unique sweep over 0..%d:" % (M - 1),
      [n for n in range(M) if all(n % m == a for a, m in system)])
print("bad pair x=1 mod 4 & x=3 mod 8 ->",
      [n for n in range(16) if n % 4 == 1 and n % 8 == 3])
```

Observed output:

```text
M = 105
a=2, m=3: M/m = 35, inverse mod m = 2, piece = 140
a=3, m=5: M/m = 21, inverse mod m = 1, piece = 63
a=2, m=7: M/m = 15, inverse mod m = 1, piece = 30
pieces sum to 233 -> x = 23 (mod 105)
check x mod (3,5,7) = [2, 3, 2]
unique sweep over 0..104: [23]
bad pair x=1 mod 4 & x=3 mod 8 -> []
```

Each piece is invisible to every other modulus (140 = 0 mod anything
dividing 35? no — 140 dies mod 5 and mod 7 because M/3 carries both),
and the empty sweep list is the non-coprime no-solution case visible
brute-force.

## 3. Euler, Fermat, and the Totient Ledger in One Pass

```python
from math import gcd

def phi(n):
    return sum(gcd(k, n) == 1 for k in range(1, n + 1))

def phi_formula(n):
    out, m, p = 1, n, 2
    while p * p <= m:
        if m % p == 0:
            k = 0
            while m % p == 0:
                m //= p
                k += 1
            out *= p ** (k - 1) * (p - 1)
        p += 1
    return out * (m - 1 if m > 1 else 1)

assert all(phi(n) == phi_formula(n) for n in range(1, 25))
print("3^40 mod 100 = %d | 2^10 mod 11 = %d (Euler / Fermat)" % (pow(3, 40, 100), pow(2, 10, 11)))
print("2^8 mod 15 = %d | 2^14 mod 15 = %d" % (pow(2, 8, 15), pow(2, 14, 15)))
print("2^80 mod 561 = %d | 2^560 mod 561 = %d" % (pow(2, 80, 561), pow(2, 560, 561)))
print("phi census: " + " ".join("%d:%d" % (n, phi(n)) for n in range(1, 25)))
print("sum phi(1..24) = %d | phi(15) = phi(3)*phi(5) = %d" % (sum(phi(n) for n in range(1, 25)), phi(3) * phi(5)))
```

Observed output:

```text
3^40 mod 100 = 1 | 2^10 mod 11 = 1 (Euler / Fermat)
2^8 mod 15 = 1 | 2^14 mod 15 = 4
2^80 mod 561 = 1 | 2^560 mod 561 = 1
phi census: 1:1 2:1 3:2 4:2 5:4 6:2 7:6 8:4 9:6 10:4 11:10 12:4 13:12 14:6 15:8 16:8 17:16 18:6 19:18 20:8 21:12 22:10 23:22 24:8
sum phi(1..24) = 180 | phi(15) = phi(3)*phi(5) = 8
```

The assert line is the real check — brute coprime counting and the
factorization product agree on all 24 rows before anything prints.
