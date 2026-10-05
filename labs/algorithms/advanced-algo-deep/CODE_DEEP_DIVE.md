# CODE_DEEP_DIVE — Advanced Algorithms Deep Track
> Java implementation + pitfalls. Track `advanced-algo-deep`.

## Canonical pattern: automaton + modular arithmetic
```java
import java.math.BigInteger;
public final class Deep {
    public static long modPow(long a, long d, long m) {
        long r = 1 % m; a %= m;
        while (d > 0) {
            if ((d & 1) == 1) r = mul(r, a, m);
            a = mul(a, a, m); d >>= 1;
        }
        return r;
    }
    static long mul(long a, long b, long m) {
        return BigInteger.valueOf(a).multiply(BigInteger.valueOf(b))
            .mod(BigInteger.valueOf(m)).longValue();
    }
    // Miller-Rabin witness loop (bases depend on bit-length)
    public static boolean isPrime(long n) {
        if (n < 2) return false;
        for (long p : new long[]{2,3,5,7,11,13,17,19,23,29,31,37})
            if (n % p == 0) return n == p;
        long d = n - 1; int s = 0;
        while ((d & 1) == 0) { d >>= 1; s++; }
        for (long a : new long[]{2, 325, 9375, 28178, 450775, 9780504, 1795265022L}) {
            if (a % n == 0) continue;
            long x = modPow(a, d, n);
            if (x == 1 || x == n - 1) continue;
            boolean comp = true;
            for (int r = 1; r < s; r++) {
                x = mul(x, x, n);
                if (x == n - 1) { comp = false; break; }
            }
            if (comp) return false;
        }
        return true;
    }
}
```

## Aho-Corasick BFS skeleton
```java
// nodes: int[26] next (or Map), int link, List<Integer> out
// build: queue root children (link=0); pop v: for c: u=go(v,c)
//   link = u missing ? go(link(v),c) : ...; merge out lists
// Pitfall: build links in BFS order, else links point to unfinished nodes.
```

## Parallel prefix (ForkJoin) sketch
```java
// class Prefix extends RecursiveAction { lo, hi, threshold=2048
//   if small: sequential scan; else fork left/right, then fix-up offset }
// Pitfall: forgetting the down-sweep offset add loses half the array.
```

## Pitfalls table
| Pitfall | Symptom | Fix |
|---|---|---|
| long overflow in modMul | wrong prime verdict | BigInteger mul or m < 2^32 guard |
| Carmichael reliance on Fermat only | composites pass | Miller-Rabin witnesses |
| Fail links built DFS | missed matches | BFS order build |
| Hull collinear mishandled | extra/missing points | decide ≤0 vs <0 policy + test |
| Bit DP wrong mask order | stale transitions | iterate masks ascending |
| ForkJoin no threshold | slower than serial | threshold 1k-10k + benchmark |
| Shared Random across threads | contention/bias | ThreadLocalRandom |
| Greedy without ratio test | silently bad cover | assert H(d) bound on fixtures |
| Strassen always-on | slower at small n | crossover + fallback |
| FFT rounding | off-by-one conv | round() + NTT for exactness |

## Testing
- Fuzz Miller-Rabin vs BigInteger.isProbablePrime on 10k random odds.
- Fuzz Aho vs naive indexOf on random texts/patterns.
- Hull: verify CCW + all points inside/on.
- Parallel prefix: compare vs sequential on 1M elements.

## Performance notes
- BigInteger mul is the hotspot; Montgomery form for production.
- Automaton: array goto for alphabet ≤ 26, map otherwise.
- Bit DP: short/int arrays to fit cache; iterate masks outer loop.

## Review checklist
- [ ] Witness loop correct. [ ] BFS order. [ ] Threshold tuned.
- [ ] Overflow guards. [ ] Fuzz green.
