# Code Deep Dive — Number Theory Advanced

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.math.BigInteger;

public final class NumTheory {
    public static long gcd(long a, long b) { while (b != 0) { long t = a % b; a = b; b = t; } return a; }

    /** Returns {g, s, t} with s*a + t*b = g. */
    public static long[] xgcd(long a, long b) {
        if (b == 0) return new long[] { a, 1, 0 };
        long[] q = xgcd(b, a % b);
        return new long[] { q[0], q[2], q[1] - (a / b) * q[2] };
    }

    public static long modPow(long a, long e, long m) {
        long acc = 1 % m;
        a %= m; if (a < 0) a += m;
        while (e > 0) {
            if ((e & 1) == 1) acc = (acc * a) % m;
            a = (a * a) % m;
            e >>= 1;
        }
        return acc;
    }

    public static long modInverse(long a, long m) {
        long[] r = xgcd(a, m);
        if (r[0] != 1) throw new ArithmeticException("no inverse");
        return (r[1] % m + m) % m;
    }

    /** Miller–Rabin with k random bases; Monte Carlo with error <= 4^-k. */
    public static boolean isProbablePrime(long n, int k) {
        if (n < 2) return false;
        for (long p : new long[] {2,3,5,7,11,13,17,19,23,29,31,37})
            if (n % p == 0) return n == p;
        long d = n - 1; int s = 0;
        while ((d & 1) == 0) { d >>= 1; s++; }
        java.util.Random rnd = new java.util.Random(n);
        outer: for (int i = 0; i < k; i++) {
            long a = 2 + Math.floorMod(rnd.nextLong(), n - 3);
            long x = modPow(a, d, n);
            if (x == 1 || x == n - 1) continue;
            for (int r = 1; r < s; r++) {
                x = (x * x) % n;
                if (x == n - 1) continue outer;
            }
            return false;
        }
        return true;
    }
}
```

## Pitfalls

- Binary % keeps the dividend's sign — always renormalise with (x % m + m) % m.
- Reducing the exponent mod φ(m) without checking gcd(a,m)=1.
- Overflow in a*b % m when a,b are near 10⁹ — switch to BigInteger.modPow.
- Miller–Rabin is Monte Carlo; a composite can pass a chosen base set.
- In modPow, starting acc at 1 instead of 1 % m breaks m == 1.
- Treating a probable prime from k rounds as certain for cryptographic sizes without enough rounds.

## Why the bounds hold

- **gcd**: Θ(log min(a,b)) time, Θ(1) — halves the larger argument within two steps.
- **xgcd/Bézout**: Θ(log min(a,b)) time, Θ(1) — carries (x,y) through the recursion.
- **modPow**: Θ(log e) multiplies time, Θ(1) — reduce after every multiply.
- **Sieve to n**: Θ(n log log n) time, Θ(n) — start marking at p².
- **Miller–Rabin**: Θ(k·log³ n) time, Θ(1) — error ≤ 4⁻ᵏ.
- **CRT, r moduli**: Θ(r²) time, Θ(r) — pairwise inverse via extended Euclid.

## Takeaway

# Theory — Number Theory Advanced
