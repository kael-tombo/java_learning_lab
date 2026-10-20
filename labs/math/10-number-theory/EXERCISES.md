# Exercises — Number Theory, Worked

Five problems; every numeric claim was confirmed by a run before
being written down.

## Problem 1. Canonical Division at Every Sign

Give the unique q and r with 0 ≤ r < |b| for a = -29, b = 7 — and
explain why (q, r) = (-3, -8) is disqualified.

**Solution**: -29 = 7·(-5) + 6. Python's divmod(-29, 7) printed
exactly (-5, 6), and 0 ≤ 6 < 7. The proposed (-3, -8) satisfies the
identity (-3)·7 + (-8) = -29 but fails the range law (remainder
negative), which is precisely the uniqueness proof's leverage: any
two solutions differ by a multiple of 7 smaller than the
possibility of another remainder, so (-3, -8) cannot coexist with a
legal (q, r).

## Problem 2. A Bezout Certificate for a Fresh Pair

Express gcd(99, 78) = 3 in the form 99x + 78y.

**Solution**: Euclid gives 99 = 1·78 + 21, 78 = 3·21 + 15,
21 = 1·15 + 6, 15 = 2·6 + 3, 6 = 2·3 + 0. Back-substituting:
3 = 15 − 2·6 = 3·15 − 2·21 = 3·78 − 11·99. So x = -11, y = 14;
the run confirmed (3, -11, 14) and re-multiplied
14·78 − 11·99 = 3. Sign slip check: 11·99 + 14·78 would give
1089 + 1092 — far from 3; both signs belong on one number.

## Problem 3. One More Inverse, By Hand

Compute 11⁻¹ mod 37 and verify.

**Solution**: 37 = 3·11 + 4, 11 = 2·4 + 3, 4 = 1·3 + 1. Backwards:
1 = 4 − 3 = 3·4 − 11 = 3·(37 − 3·11) − 11 = 3·37 − 10·11. Hence
11⁻¹ ≡ −10 ≡ 27 (mod 37); the run checked 27·11 mod 37 = 1. Note
the existence condition held: gcd(11, 37) = 1.

## Problem 4. A Three-Moduli CRT System

Solve x ≡ 1 (mod 4), x ≡ 2 (mod 7), x ≡ 3 (mod 13).

**Solution**: M = 4·7·13 = 364. Pieces a·(M/m)·(M/m)⁻¹ mod m:
for m = 4: 91 with inverse of 3 → piece 273; m = 7: 52, inverse
of 3 is 5 → 520; m = 13: 28, inverse of 2 is 7 → 588. Sum
1381 ≡ 289 (mod 364), and 289 = 17². The run printed the system
result (289, 364), the three pieces [273, 520, 588], and a brute
sweep returning only [289] — unique because coprime moduli make
the solution exact modulo 364.

## Problem 5. Programming: A CRT Solver That Knows When to Refuse

Implement `crt(system)` returning `(x mod M, M)` for coprime
moduli; test it on Problem 4's system, then handle the non-coprime
cases x ≡ 2 (mod 4) with x ≡ 4 (mod 6) and x ≡ 1 (mod 4) with
x ≡ 3 (mod 8) by brute search over lcm intervals.

**Solution**: The executed run:

```python
from math import gcd

def crt(system):
    M = 1
    for _, m in system:
        M *= m
    x = sum(a * (M // m) * pow(M // m, -1, m) for a, m in system)
    return x % M, M

print("P4 system:", crt([(1, 4), (2, 7), (3, 13)]))
print("pieces for P4:", [a * (364 // m) * pow(364 // m, -1, m) for a, m in [(1, 4), (2, 7), (3, 13)]])
print("consistent non-coprime: modulus 12 solution =",
      [n for n in range(12) if n % 4 == 2 and n % 6 == 4])
print("inconsistent: x=1 mod 4 & x=3 mod 8 ->",
      [n for n in range(16) if n % 4 == 1 and n % 8 == 3],
      "while gcd(4, 8) = %d does not divide 3-1 = 2" % gcd(4, 8))
print("P2 recheck: 14*78 - 11*99 =", 14 * 78 - 11 * 99, "| 27*11 mod 37 =", 27 * 11 % 37)
```

Output: `(289, 364)`, pieces `[273, 520, 588]`, the non-coprime but
compatible pair resolving to `[10]` (solutions live modulo lcm 12
since gcd 2 divides 4 − 2), the incompatible pair yielding `[]`
(gcd 4 does not divide 3 − 1 = 2), and the two rechecks
`3` and `1`. Existence law: x ≡ a (mod m) with x ≡ b (mod n) has
solutions iff gcd(m, n) divides a − b.
