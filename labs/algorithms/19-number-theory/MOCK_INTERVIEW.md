# Mock Interview: Number Theory: Euclid, Sieve, Modular Exponentiation
> Three worked questions on integer algorithms. Each answer is complete runnable Java; outputs below were observed.

## Q1: Compute gcd(30, 20) with Bezout coefficients via extended Euclid.
Key insight: Euclid's step gcd(a,b) = gcd(b, a mod b) shrinks the numbers geometrically (a mod b < a/2 every two steps). Unwinding the recursion expresses the gcd as 30x + 20y, which is exactly what modular inverses need.
Complexity: Time O(log min(a, b)); space O(log min(a, b)) stack.
```java
public class L19Q1Euclid {
    static long[] egcd(long a, long b) {
        if (b == 0) return new long[]{a, 1, 0};
        long[] r = egcd(b, a % b);
        return new long[]{r[0], r[2], r[1] - (a / b) * r[2]};
    }
    public static void main(String[] args) {
        long[] r = egcd(30, 20);
        System.out.println("gcd=" + r[0] + " x=" + r[1] + " y=" + r[2] + " check=" + (30 * r[1] + 20 * r[2]));
    }
}
```
Observed output: `gcd=10 x=1 y=-1 check=10`
Follow-up: How does the check value prove the coefficients, and how do you get the inverse of 20 mod 30/gcd from them?

## Q2: List all primes up to 30 with the sieve of Eratosthenes.
Key insight: Each prime p crosses out its multiples starting at p^2 (smaller multiples were already crossed by smaller primes). Summing n/p over primes gives the O(n log log n) bound - nearly linear in practice.
Complexity: Time O(n log log n); space O(n) booleans.
```java
public class L19Q2Sieve {
    public static void main(String[] args) {
        boolean[] c = new boolean[31];
        for (int i = 2; i * i <= 30; i++) if (!c[i]) for (int j = i * i; j <= 30; j += i) c[j] = true;
        String s = "";
        for (int i = 2; i <= 30; i++) if (!c[i]) s += i + " ";
        System.out.println("primes=" + s.trim());
    }
}
```
Observed output: `primes=2 3 5 7 11 13 17 19 23 29`
Follow-up: Why is starting the inner loop at i*i (not 2*i) correct, and what does it save asymptotically?

## Q3: Verify Fermat's little theorem instance 2^16 = 1 mod 17 with square-and-multiply.
Key insight: Fermat says a^(p-1) = 1 mod p for prime p and a not divisible by p. Square-and-multiply keeps every intermediate product reduced mod m, so the exponent 16 needs 4 squarings, not 16 multiplications.
Complexity: Time O(log e) modular multiplications; space O(1).
```java
public class L19Q3ModPow {
    static long mp(long x, long e, long m) {
        long r = 1;
        while (e > 0) { if ((e & 1) == 1) r = r * x % m; x = x * x % m; e >>= 1; }
        return r;
    }
    public static void main(String[] args) {
        System.out.println("2^16 mod 17=" + mp(2, 16, 17) + " 3^5 mod 7=" + mp(3, 5, 7));
    }
}
```
Observed output: `2^16 mod 17=1 3^5 mod 7=5`
Follow-up: What does 2^560 = 1 mod 561 tell you, given 561 = 3*11*17 is composite?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
