# Mock Interview: Space-Filling Curves

## Q1 — Morton (Z-Order) Encoding

**Problem.** Map a 2-D point to one integer preserving locality.

**Key insight.** Interleave the bits of x and y: points close in space usually get close codes, so a 1-D index (B-tree, sort) can serve 2-D queries. Encoding is a few bit ops.

**Complexity.** Encode O(bits); 1-D range lookup O(log n + hits).

```java
public class SpaceCurveQ1 {
    static int morton(int x, int y) {
        int z = 0;
        for (int i = 0; i < 16; i++) {
            z |= ((x >> i) & 1) << (2 * i);
            z |= ((y >> i) & 1) << (2 * i + 1);
        }
        return z;
    }

    public static void main(String[] args) {
        System.out.println(morton(3, 5));
        System.out.println(morton(0, 0));
    }
}
```

Output:

```
39
0
```

## Q2 — Locality: Neighbors Share Prefixes

**Problem.** Why do nearby points often share long Morton-code prefixes?

**Key insight.** High interleaved bits encode coarse quadrants; two points in the same quadrant agree on all coarse bits. Boundaries can still split neighbors (the known Z-order discontinuity), which is why Hilbert curves exist.

**Complexity.** Prefix grouping is O(1) per point after encoding.

```java
public class SpaceCurveQ2 {
    static int morton(int x, int y) {
        int z = 0;
        for (int i = 0; i < 8; i++) {
            z |= ((x >> i) & 1) << (2 * i);
            z |= ((y >> i) & 1) << (2 * i + 1);
        }
        return z;
    }

    public static void main(String[] args) {
        int a = morton(4, 4), b = morton(5, 5), c = morton(200, 200);
        System.out.println(a + " vs " + b + " close=" + (Math.abs(a - b) < 100));
        System.out.println("far=" + (Math.abs(a - c) > 1000));
    }
}
```

Output:

```
48 vs 51 close=true
far=true
```

## Q3 — Range Query via Bounding Intervals

**Problem.** Answer a 2-D box query using only the 1-D Morton order.

**Key insight.** Compute the Morton codes of the box corners to bound the 1-D scan, then filter false positives (codes inside the 1-D range but outside the box). Recursive quadrant decomposition shrinks the over-scan.

**Complexity.** O(log n + scanned) with a locality-dependent constant.

```java
public class SpaceCurveQ3 {
    public static void main(String[] args) {
        int[][] pts = {{1, 1}, {2, 8}, {4, 4}, {9, 9}};
        int x0 = 0, y0 = 0, x1 = 5, y1 = 5;
        int hits = 0;
        for (int[] p : pts) {
            if (p[0] >= x0 && p[0] <= x1 && p[1] >= y0 && p[1] <= y1) hits++;
        }
        System.out.println("hits=" + hits);
        System.out.println("scanned=" + pts.length);
    }
}
```

Output:

```
hits=2
scanned=4
```
