# Mock Interview: Advanced Number Theory
> Three questions on primality testing and factoring. Everything here is classical integer arithmetic; base choices are stated exactly as run.
## Q1: binary modular exponentiation
Problem: compute 3^200 mod 1000, verify 2^16 = 1 mod 17, and test base 2 on 341.
Key insight: square-and-multiply keeps intermediates below m^2; Fermat holds at 17, while 341 = 11 x 31 still gives 2^340 = 1 mod 341, a base-2 pseudoprime that motivates stronger tests.
Complexity: O(log e) multiplies, O(1) memory.
```java
public class L39Q1 {
    static long modPow(long b, long e, long m){ long r = 1 % m; b %= m; while (e > 0){ if ((e&1)==1) r = (r*b)%m; b = (b*b)%m; e >>= 1; } return r; }
    public static void main(String[] a){
        System.out.println("powmod(3,200,1000)=" + modPow(3,200,1000));
        System.out.println("fermat_ok=" + (modPow(2,16,17) == 1) + " pseudo341=" + (modPow(2,340,341) == 1));
    }
}
```
Observed output:
```
powmod(3,200,1000)=1
fermat_ok=true pseudo341=true
```
Follow-up: why must the multiplication use long (or wider) before the mod?
## Q2: Miller-Rabin, fixed bases
Problem: run Miller-Rabin with bases {2, 7, 61} on 17, 561, 2047, 7919.
Key insight: writing n - 1 = d*2^s and checking the witness chain catches composites Fermat misses: Carmichael number 561 and 2047 = 23 x 89 both report COMPOSITE; the stated bases are a published deterministic set for the 32-bit range.
Complexity: O(k log^3 n) for k bases, O(1) memory.
```java
public class L39Q2 {
    static long modPow(long b,long e,long m){ long r=1%m; b%=m; while(e>0){ if((e&1)==1) r=(r*b)%m; b=(b*b)%m; e>>=1; } return r; }
    static boolean isPrime(int n){
        if (n < 2) return false;
        for (int p : new int[]{2,3,5,7,11,13,17,19,23,29}){ if (n==p) return true; if (n%p==0) return false; }
        int d = n-1, s = 0; while ((d&1)==0){ d>>=1; s++; }
        for (int a : new int[]{2,7,61}){
            if (a % n == 0) continue;
            long x = modPow(a, d, n); if (x==1 || x==n-1) continue;
            boolean ok = false; for (int r=1;r<s;r++){ x=(x*x)%n; if (x==n-1){ ok=true; break; } }
            if (!ok) return false;
        }
        return true;
    }
    public static void main(String[] a){ for (int n : new int[]{17,561,2047,7919}) System.out.println(n + "=" + (isPrime(n) ? "PRIME" : "COMPOSITE")); }
}
```
Observed output:
```
17=PRIME
561=COMPOSITE
2047=COMPOSITE
7919=PRIME
```
Follow-up: what is a Miller-Rabin witness, and why do Carmichael numbers still fail the test?
## Q3: Pollard Rho concept demo
Problem: factor 8051 with f(x) = x^2 + 1 and Floyd cycling from x = y = 2.
Key insight: the gcd(|x - y|, n) exposes a factor when the two walks collide modulo a hidden prime factor; here it returns 97 with cofactor 83.
Complexity: heuristic, roughly O(n^(1/4)); trial-divide small primes first.
```java
public class L39Q3 {
    static long gcd(long a, long b){ return b==0 ? a : gcd(b, a%b); }
    public static void main(String[] a){
        long n = 8051, x = 2, y = 2, d = 1;
        while (d == 1){ x = (x*x+1)%n; y = (y*y+1)%n; y = (y*y+1)%n; d = gcd(Math.abs(x-y), n); }
        System.out.println("factor=" + d + " cofactor=" + (n/d));
    }
}
```
Observed output:
```
factor=97 cofactor=83
```
Follow-up: what do you change when the walk returns d = n (restart with a new constant)?
## Pass checklist
- [ ] Factor 341 and 2047 by hand-followable trial division to confirm COMPOSITE claims.
- [ ] Verify 8051 = 97 x 83 with plain multiplication.
- [ ] Never present the fixed bases as valid beyond the stated 32-bit range.
