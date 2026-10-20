# Code Deep Dive — Extended Euclid, CRT Assembly, Prime-Modulus Laws

Two runnable Python programs (stdlib only); output blocks are untouched from the runs.

## 1. Extended Euclid and Modular Inverses

```python
def ext_gcd(a, b):
    if b == 0: return (a, 1, 0)
    g, x, y = ext_gcd(b, a % b)
    return (g, y, x - (a // b) * y)

for (a, b) in [(240, 46), (57, 29), (101, 13)]:
    g, x, y = ext_gcd(a, b)
    print("ext_gcd(%d, %d): g = %d, x = %d, y = %d  check %d*%d + %d*%d = %d: %s" %
          (a, b, g, x, y, a, x, b, y, a * x + b * y, a * x + b * y == g))
print("division steps: 240 = %d*46 + %d;  46 = %d*%d + %d" % (240 // 46, 240 % 46, 46 // 10, 10, 46 % 10))

def modinv(a, m):
    g, x, _ = ext_gcd(a % m, m)
    return None if g != 1 else x % m

for (a, m) in [(17, 43), (7, 26), (11, 15), (6, 15)]:
    inv = modinv(a, m)
    if inv is None:
        print("no inverse for %d mod %d (gcd = %d != 1)" % (a, m, ext_gcd(a, m)[0]))
    else:
        print("%d^-1 mod %d = %d;  %d * %d = %d = %d * %d + %d" %
              (a, m, inv, a, inv, a * inv, (a * inv) // m, m, a * inv % m))
```

Observed output:

```text
ext_gcd(240, 46): g = 2, x = -9, y = 47  check 240*-9 + 46*47 = 2: True
ext_gcd(57, 29): g = 1, x = -1, y = 2  check 57*-1 + 29*2 = 1: True
ext_gcd(101, 13): g = 1, x = 4, y = -31  check 101*4 + 13*-31 = 1: True
division steps: 240 = 5*46 + 10;  46 = 4*10 + 6
17^-1 mod 43 = 38;  17 * 38 = 646 = 15 * 43 + 1
7^-1 mod 26 = 15;  7 * 15 = 105 = 4 * 26 + 1
11^-1 mod 15 = 11;  11 * 11 = 121 = 8 * 15 + 1
no inverse for 6 mod 15 (gcd = 3 != 1)
```

## 2. CRT, the Consistency Gate, Fermat, and Euler's φ

```python
import math

def ext_gcd(a, b):
    if b == 0: return (a, 1, 0)
    g, x, y = ext_gcd(b, a % b)
    return (g, y, x - (a // b) * y)

def crt(r, moduli):
    M = math.prod(moduli)
    ts = [ai * (M // mi) * (ext_gcd((M // mi) % mi, mi)[1] % mi) for ai, mi in zip(r, moduli)]
    return M, sum(ts) % M, ts

M, x, ts = crt([2, 3, 2], [3, 5, 7])
print("terms:", ts, " raw:", sum(ts), " x = %d mod %d" % (x, M))
print("x verifies: mod 3 = %d mod 5 = %d mod 7 = %d  |  23 + 105 = %d: mod 3 = %d mod 5 = %d mod 7 = %d" % (x % 3, x % 5, x % 7, x + 105, (x + 105) % 3, (x + 105) % 5, (x + 105) % 7))
print("gate rows: diff 8 %% 4 = %d -> solvable: %s   |   diff 1 %% 4 = %d -> solvable: %s" % (8 % 4, 8 % 4 == 0, 1 % 4, 1 % 4 == 0))
print("Fermat: 2^6=64 ->", (2 ** 6) % 7, " mod 7;  2^10=1024 ->", (2 ** 10) % 11, " mod 11;  2^3 mod 4 =", (2 ** 3) % 4, "(composite modulus)")

def phi_form(n):
    r, m = n, n
    for pp in range(2, n // 2 + 1):
        if m % pp == 0:
            r -= r // pp
            while m % pp == 0: m //= pp
    return r - r // m if m > 1 else r

for n, a in ((15, 7), (36, 11), (100, 3)):
    f, c = phi_form(n), sum(1 for k in range(1, n + 1) if math.gcd(k, n) == 1)
    print("phi(%d) = %d (census %d, equal: %s)" % (n, f, c, f == c))
    print("%d^%d mod %d = %d (gcd = %d)" % (a, f, n, pow(a, f, n), math.gcd(a, n)))
print("phi(36) formula: 36 = 2^2 * 3^2 -> (4-2)*(9-3) =", (4 - 2) * (9 - 3))
```

Observed output:

```text
terms: [140, 63, 30]  raw: 233  x = 23 mod 105
x verifies: mod 3 = 2 mod 5 = 3 mod 7 = 2  |  23 + 105 = 128: mod 3 = 2 mod 5 = 3 mod 7 = 2
gate rows: diff 8 % 4 = 0 -> solvable: True   |   diff 1 % 4 = 1 -> solvable: False
Fermat: 2^6=64 -> 1  mod 7;  2^10=1024 -> 1  mod 11;  2^3 mod 4 = 0 (composite modulus)
phi(15) = 8 (census 8, equal: True)
7^8 mod 15 = 1 (gcd = 1)
phi(36) = 12 (census 12, equal: True)
11^12 mod 36 = 1 (gcd = 1)
phi(100) = 40 (census 40, equal: True)
3^40 mod 100 = 1 (gcd = 1)
phi(36) formula: 36 = 2^2 * 3^2 -> (4-2)*(9-3) = 12
```

Every tile of the CRT assembly is printed — terms 140, 63, 30 — and
the gate rows show one solvable and one dead system.
