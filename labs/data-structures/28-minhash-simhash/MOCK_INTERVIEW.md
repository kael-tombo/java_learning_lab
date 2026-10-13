# Mock Interview: MinHash and SimHash

## Q1 — Jaccard via MinHash Signatures

**Problem.** Estimate set similarity without comparing full sets.

**Key insight.** Under a random permutation, P(both sets share the same minimum) equals the Jaccard similarity. Repeat with k hash functions: the fraction of equal minima estimates Jaccard with error O(1/sqrt(k)).

**Complexity.** Signature O(k) per set; compare O(k).

```java
import java.util.Set;

public class MinHashQ1 {
    static int hash(String s, int seed) {
        return (s.hashCode() * (0x9e3779b9 + seed * 0x85ebca6b)) ^ (seed * 97);
    }

    public static void main(String[] args) {
        Set<String> a = Set.of("cat", "dog", "fish");
        Set<String> b = Set.of("cat", "dog", "bird");
        int k = 64, agree = 0;
        for (int i = 0; i < k; i++) {
            int ma = Integer.MAX_VALUE, mb = Integer.MAX_VALUE;
            for (String s : a) ma = Math.min(ma, hash(s, i));
            for (String s : b) mb = Math.min(mb, hash(s, i));
            if (ma == mb) agree++;
        }
        System.out.printf("%.2f%n", agree / (double) k);
    }
}
```

Output:

```
0.48
```

## Q2 — SimHash Near-Duplicate Detection

**Problem.** Fingerprint documents so near-duplicates have nearby fingerprints.

**Key insight.** Sum +1/-1 weighted token hashes into an accumulator vector, then take sign bits. Similar documents differ in few bits (small Hamming distance), unlike cryptographic hashes where one change flips everything.

**Complexity.** Fingerprint O(tokens * bits); compare O(1) words.

```java
public class MinHashQ2 {
    static long simhash(String[] tokens) {
        long[] acc = new long[16];
        for (String t : tokens) {
            int h = t.hashCode();
            for (int i = 0; i < 16; i++) {
                acc[i] += ((h >> i) & 1) == 1 ? 1 : -1;
            }
        }
        long fp = 0;
        for (int i = 0; i < 16; i++) if (acc[i] > 0) fp |= (1L << i);
        return fp;
    }

    public static void main(String[] args) {
        long a = simhash(new String[]{"the", "cat", "sat"});
        long b = simhash(new String[]{"the", "cat", "sat!"});
        long c = simhash(new String[]{"quantum", "zebras", "orbit"});
        System.out.println((Long.bitCount(a ^ b) < Long.bitCount(a ^ c)) + "," + Long.bitCount(a ^ a));
    }
}
```

Output:

```
true,0
```

## Q3 — Choosing k (MinHash) and Threshold (SimHash)

**Problem.** How many MinHash functions, and what Hamming threshold?

**Key insight.** MinHash error shrinks as 1/sqrt(k): k = 128 gives roughly +/-0.09 bands. SimHash thresholds are empirical: Hamming distance <= 3 on 64 bits is the classic near-dup cutoff; validate on labeled pairs.

**Complexity.** Bigger k costs linear compare time; smaller thresholds cost recall.

```java
public class MinHashQ3 {
    public static void main(String[] args) {
        for (int k : new int[]{64, 128, 256}) {
            System.out.printf("k=%d err~%.3f%n", k, 1.0 / Math.sqrt(k));
        }
    }
}
```

Output:

```
k=64 err~0.125
k=128 err~0.088
k=256 err~0.063
```
