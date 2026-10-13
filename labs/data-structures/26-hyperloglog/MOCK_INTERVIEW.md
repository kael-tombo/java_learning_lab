# Mock Interview: HyperLogLog

## Q1 — Leading-Zero (rho) Estimation Idea

**Problem.** Estimate distinct count from a tiny sketch.

**Key insight.** For uniform hashes, P(leading zeros >= k) = 2^-k, so the max rho over n hashes is about log2 n. HLL keeps m registers of max-rho per bucket and takes a harmonic mean: small memory, ~1.04/sqrt(m) relative error.

**Complexity.** Add O(1), estimate O(m), space O(m) bytes.

```java
public class HllQ1 {
    static int rho(int h) {
        int r = 1;
        while ((h & 1) == 0 && r < 31) { h >>>= 1; r++; }
        return r;
    }

    public static void main(String[] args) {
        System.out.println(rho(1));
        System.out.println(rho(8));
        System.out.println(rho(0b11000));
    }
}
```

Output:

```
1
4
4
```

## Q2 — Bucketed Registers Demo

**Problem.** Show how bucketing fixes the single-max variance problem.

**Key insight.** One global max is dominated by the luckiest hash. Splitting hashes into m = 2^p buckets by their first p bits and averaging per-bucket maxima stabilizes the estimate; harmonic mean resists single-bucket outliers.

**Complexity.** Same O(1) add; p = 14 (m = 16384) is the classic default.

```java
public class HllQ2 {
    public static void main(String[] args) {
        int p = 4, m = 1 << p;
        int[] reg = new int[m];
        String[] items = {"a", "b", "c", "a", "d", "b"};
        for (String s : items) {
            int h = s.hashCode() * 0x9e3779b9;
            int bucket = (h >>> 28) & (m - 1);
            int w = (h << p) | (1 << 27);
            int r = Integer.numberOfLeadingZeros(w) + 1;
            if (r > reg[bucket]) reg[bucket] = r;
        }
        int used = 0;
        for (int v : reg) if (v > 0) used++;
        System.out.println("registers=" + m);
        System.out.println("nonempty=" + used);
    }
}
```

Output:

```
registers=16
nonempty=4
```

## Q3 — When HLL Is the Wrong Tool

**Problem.** A teammate proposes HLL for exact billing counts. Respond.

**Key insight.** HLL is approximate (percent-level error) and mergeable/duplicate-insensitive; billing needs exactness, so use exact counting or a sketch with one-sided guarantees you can bound (e.g. Count-Min for upper bounds). HLL shines for distinct visitors, reach, cardinality dashboards.

**Complexity.** Exact counting costs O(n) memory; HLL costs O(m) with bounded relative error.

```java
public class HllQ3 {
    public static void main(String[] args) {
        for (int p : new int[]{4, 10, 14}) {
            double err = 1.04 / Math.sqrt(1 << p);
            System.out.printf("p=%d err=%.4f%n", p, err);
        }
    }
}
```

Output:

```
p=4 err=0.2600
p=10 err=0.0325
p=14 err=0.0081
```
