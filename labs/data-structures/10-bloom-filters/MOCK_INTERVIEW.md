# Mock Interview: Bloom Filters

## Q1 — False-Positive Rate Formula

**Problem.** A Bloom filter has m bits, k hashes, n inserted elements. Compute the standard FPR estimate.

**Key insight.** A bit stays 0 with probability about e^(-kn/m), so all k probes hit 1s with probability (1 - e^(-kn/m))^k. This is an estimate for a well-mixed hash family.

**Complexity.** Add/query O(k), space O(m) bits regardless of n.

```java
public class BloomQ1 {
    public static double fpr(long m, int k, long n) {
        return Math.pow(1 - Math.exp(-(double) k * n / m), k);
    }

    public static void main(String[] args) {
        System.out.printf("%.4f%n", fpr(9585, 7, 1000));
    }
}
```

Output:

```
0.0100
```

## Q2 — Optimal Number of Hashes

**Problem.** Given m bits and n elements, how many hash functions minimize the FPR?

**Key insight.** Differentiate the FPR estimate: optimum k = (m/n) ln 2. Rounding to an integer is fine.

**Complexity.** Same O(k) ops; choosing k is O(1) arithmetic.

```java
public class BloomQ2 {
    public static void main(String[] args) {
        long m = 9585, n = 1000;
        double kOpt = (m / (double) n) * Math.log(2);
        System.out.printf("%.2f%n", kOpt);
        System.out.println(Math.max(1, (int) Math.round(kOpt)));
    }
}
```

Output:

```
6.64
7
```

## Q3 — BitSet Demo: No False Negatives

**Problem.** Show the core guarantee: a Bloom filter never reports a present item as absent.

**Key insight.** Query returns "possibly present" only if all k bits are set; inserted items set all k, so they always query true. Errors are one-sided (false positives only), and deletion is unsupported.

**Complexity.** O(k) per op.

```java
import java.util.BitSet;

public class BloomQ3 {
    static int[] hashes(String s, int k, int m) {
        int[] out = new int[k];
        int h1 = s.hashCode(), h2 = h1 * 0x5bd1e995 + 0x12345;
        for (int i = 0; i < k; i++) {
            out[i] = Math.floorMod(h1 + i * h2, m);
        }
        return out;
    }

    public static void main(String[] args) {
        int m = 256, k = 3;
        BitSet bits = new BitSet(m);
        for (int b : hashes("apple", k, m)) bits.set(b);
        boolean present = true;
        for (int b : hashes("apple", k, m)) present &= bits.get(b);
        boolean absent = true;
        for (int b : hashes("qqq-zzz-never-added", k, m)) absent &= bits.get(b);
        System.out.println(present);
        System.out.println(absent);
    }
}
```

Output:

```
true
false
```
