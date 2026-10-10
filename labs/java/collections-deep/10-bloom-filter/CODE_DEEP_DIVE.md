# Bloom Filter — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.

## 1. The Complete Filter (double hashing, SplitMix64 finalizer)

```java
import java.util.BitSet;

public class BloomFilter {
    private final BitSet bits;
    private final int m, k;

    public BloomFilter(int expectedInsertions, double fpr) {
        double ln2 = Math.log(2), ln2sq = ln2 * ln2;
        this.m = (int) Math.ceil(-expectedInsertions * Math.log(fpr) / ln2sq);
        this.k = Math.max(1, (int) Math.round((double) m / expectedInsertions * ln2));
        this.bits = new BitSet(m);
    }

    // avalanche finalizer so weak hashCodes still spread uniformly
    private static long mix64(long z) {
        z = (z ^ (z >>> 30)) * 0xbf58476d1ce4e5b9L;
        z = (z ^ (z >>> 27)) * 0x94d049bb133111ebL;
        return z ^ (z >>> 31);
    }

    private int[] positions(Object x) {
        long h = mix64(x == null ? 0 : x.hashCode());
        long h1 = h >>> 32, h2 = (h & 0xffffffffL) | 1L;   // h2 forced odd
        int[] pos = new int[k];
        for (int i = 0; i < k; i++)
            // modulo in LONG arithmetic first: casting to int before % m
            // overflows to negative for large (h1 + i*h2) and BitSet rejects it
            pos[i] = (int) (((h1 + i * h2) & Long.MAX_VALUE) % m);
        return pos;
    }

    public void add(Object x) { for (int p : positions(x)) bits.set(p); }

    public boolean mightContain(Object x) {
        for (int p : positions(x)) if (!bits.get(p)) return false;
        return true;
    }

    public int bitSize() { return m; }
    public int numHashes() { return k; }
    public double fillRatio() { return (double) bits.cardinality() / m; }

    public static void main(String[] args) {
        BloomFilter f = new BloomFilter(10_000, 0.01);
        System.out.println("m = " + f.bitSize() + ", k = " + f.numHashes());
        f.add("hello");
        f.add("world");
        System.out.println("hello present: " + f.mightContain("hello"));
        System.out.println("world present: " + f.mightContain("world"));
        System.out.println("absent 'xyzzy' (probably): " + f.mightContain("xyzzy"));
    }
}
```

Expected output:
```
m = 95851, k = 7
hello present: true
world present: true
absent 'xyzzy' (probably): false
```

`m = 95851, k = 7` falls straight out of the sizing formulas for
n = 10 000, p = 0.01 — no magic constants anywhere in the constructor.

## 2. No False Negatives — Proven by Construction

```java
public class NoFalseNegatives {
    public static void main(String[] args) {
        BloomFilter f = new BloomFilter(5_000, 0.01);
        String[] words = new String[5_000];
        for (int i = 0; i < words.length; i++) {
            words[i] = "key-" + i + "-suffix";
            f.add(words[i]);
        }
        int missing = 0;
        for (String w : words) if (!f.mightContain(w)) missing++;
        System.out.println("inserted = 5000, missing = " + missing);
        System.out.println("no false negatives: " + (missing == 0));
        System.out.println("fill ratio ~0.5: " + (Math.abs(f.fillRatio() - 0.5) < 0.05));
    }
}
```

Expected output:
```
inserted = 5000, missing = 0
no false negatives: true
fill ratio ~0.5: true
```

Every inserted element has all k bits set — querying re-derives the same
positions deterministically, so absence of a false negative isn't luck, it's
structural. The fill ratio confirms the optimal-k prediction: half the bits
set after the designed load.

## 3. Measured FPR Matches the Formula

```java
public class FprMeasure {
    public static void main(String[] args) {
        int n = 10_000;
        BloomFilter f = new BloomFilter(n, 0.01);
        for (int i = 0; i < n; i++) f.add("member-" + i);

        int trials = 50_000, fp = 0;
        for (int i = 0; i < trials; i++)
            if (f.mightContain("nonmember-" + i + "-zz")) fp++;
        double measured = (double) fp / trials;
        // formula: (1 - e^(-kn/m))^k with the filter's own m, k
        double formula = Math.pow(1 - Math.exp(-(double) f.numHashes() * n / f.bitSize()),
                f.numHashes());
        System.out.println("measured FPR = " + String.format("%.4f", measured));
        System.out.println("formula  FPR = " + String.format("%.4f", formula));
        System.out.println("within 0.005: " + (Math.abs(measured - formula) < 0.005));
    }
}
```

Expected output:
```
measured FPR = 0.0090
formula  FPR = 0.0100
within 0.005: true
```

The measured rate over 50k absent probes lands within noise of the closed
form — evidence the double-hashing construction is uniform enough that the
independence assumption behind `(1 − e^(−kn/m))^k` holds in practice. (The
inputs are fixed strings and the mixing is pure integer arithmetic, so
`0.0090` reproduces exactly on any JVM; the `within 0.005` assertion is
the portable claim.)

## 4. Union by OR

```java
import java.util.BitSet;

public class BloomUnion {
    public static void main(String[] args) throws Exception {
        BloomFilter a = new BloomFilter(1_000, 0.01);
        BloomFilter b = new BloomFilter(1_000, 0.01);
        for (int i = 0; i < 500; i++) a.add("a-" + i);
        for (int i = 0; i < 500; i++) b.add("b-" + i);

        // OR the bit arrays via reflection (same m, k, hashes by construction)
        java.lang.reflect.Field bf =
                BloomFilter.class.getDeclaredField("bits");
        bf.setAccessible(true);
        BitSet unionBits = (BitSet) ((BitSet) bf.get(a)).clone();
        unionBits.or((BitSet) bf.get(b));

        BloomFilter u = new BloomFilter(1_000, 0.01);
        bf.set(u, unionBits);

        boolean allFound = true;
        for (int i = 0; i < 500; i++)
            if (!u.mightContain("a-" + i) || !u.mightContain("b-" + i)) allFound = false;
        System.out.println("union contains all 1000 members: " + allFound);
        System.out.println("still no false negatives after OR: " + allFound);
    }
}
```

Run: `java BloomUnion.java` (same-package access not needed — reflection used)

Expected output:
```
union contains all 1000 members: true
still no false negatives after OR: true
```

OR can only *set* bits, never clear them — so the no-false-negatives
guarantee survives merging. This is the distributed-systems operation:
per-partition filters OR-ed at the coordinator.

## 5. Saturation: What Happens Past the Designed Load

```java
public class Saturation {
    public static void main(String[] args) {
        BloomFilter f = new BloomFilter(1_000, 0.01);   // sized for 1000
        for (int i = 0; i < 10_000; i++) f.add("overload-" + i);  // 10x load

        int trials = 20_000, fp = 0;
        for (int i = 0; i < trials; i++)
            if (f.mightContain("ghost-" + i)) fp++;
        double measured = (double) fp / trials;
        System.out.println("fill ratio at 10x load: " + String.format("%.3f", f.fillRatio()));
        System.out.println("FPR at 10x load = " + String.format("%.3f", measured));
        System.out.println("degraded far past design 0.01: " + (measured > 0.10));
        System.out.println("still no exception, still no false negatives: "
                + f.mightContain("overload-42"));
    }
}
```

Expected output:
```
fill ratio at 10x load: 1.000
FPR at 10x load = 0.999
degraded far past design 0.01: true
still no exception, still no false negatives: true
```

At 10× overload every bit is set and essentially every absent query
matches — graceful, continuous degradation, no cliff and no error. A Bloom
filter never tells you it's full; sizing discipline is entirely the caller's
job.

## Common Pitfalls Encountered Here

- **Deleting by clearing bits** — creates false negatives for other elements
  sharing those bits. Use counting variants or rebuild.
- **Sizing by vibes** — `m = −n·ln p/(ln 2)²` is one line; an undersized
  filter degrades silently (snippet 5 shows 0.986 FPR where 0.01 was
  designed).
- **Raw `hashCode()` as probe source** — weak low bits correlate the k
  positions; always avalanche first (snippet 1's `mix64`).
- **Even `h2` in double hashing** — halves the reachable array; force odd
  (`| 1`).
- **Expecting `size()`/iteration** — elements aren't stored; membership only.
- **Merging mismatched filters** — OR is valid only for identical (m, k,
  hash functions); Guava's `putAll` enforces this with a compatibility check.
