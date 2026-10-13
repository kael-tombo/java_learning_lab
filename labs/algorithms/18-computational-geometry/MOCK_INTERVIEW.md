# Mock Interview: Computational Geometry: Orientation, Segments, Convex Hull
> Three worked questions on exact geometric predicates. Each answer is complete runnable Java; outputs below were observed.

## Q1: Classify three turns with the cross-product orientation test.
Key insight: cross(o,a,b) = (a-o) x (b-o): positive means counter-clockwise, negative clockwise, zero collinear. One integer predicate underlies segment intersection, hulls, and point-in-polygon - get its sign convention right once.
Complexity: Time O(1); space O(1). Exact with integers; no floating point needed.
```java
public class L18Q1Orient {
    static long cross(int[] o, int[] a, int[] b) {
        return (long) (a[0] - o[0]) * (b[1] - o[1]) - (long) (a[1] - o[1]) * (b[0] - o[0]);
    }
    public static void main(String[] args) {
        long ccw = cross(new int[]{0, 0}, new int[]{1, 0}, new int[]{1, 1});
        long cw = cross(new int[]{0, 0}, new int[]{1, 0}, new int[]{1, -1});
        long col = cross(new int[]{0, 0}, new int[]{1, 1}, new int[]{2, 2});
        System.out.println("ccw=" + ccw + " cw=" + cw + " collinear=" + col);
    }
}
```
Observed output: `ccw=1 cw=-1 collinear=0`
Follow-up: Why cast to long before multiplying, and which coordinate magnitude overflows int products?

## Q2: Test two segment pairs for proper intersection.
Key insight: Segments p1p2 and p3p4 cross properly iff p1, p2 straddle the line through p3p4 AND vice versa - four orientation signs, no division. Collinear overlap needs a separate bounding-box check, which this strict version excludes by design.
Complexity: Time O(1); space O(1).
```java
public class L18Q2SegInt {
    static long cross(int[] o, int[] a, int[] b) {
        return (long) (a[0] - o[0]) * (b[1] - o[1]) - (long) (a[1] - o[1]) * (b[0] - o[0]);
    }
    static boolean inter(int[] p1, int[] p2, int[] p3, int[] p4) {
        long d1 = cross(p3, p4, p1), d2 = cross(p3, p4, p2);
        long d3 = cross(p1, p2, p3), d4 = cross(p1, p2, p4);
        return ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0));
    }
    public static void main(String[] args) {
        boolean c = inter(new int[]{0, 0}, new int[]{2, 2}, new int[]{0, 2}, new int[]{2, 0});
        boolean d = inter(new int[]{0, 0}, new int[]{1, 1}, new int[]{2, 2}, new int[]{3, 3});
        System.out.println("cross=" + c + " disjoint=" + d);
    }
}
```
Observed output: `cross=true disjoint=false`
Follow-up: Extend this to report collinear overlap: what bounding-box test on the endpoints is needed?

## Q3: Compute the convex hull of 6 points with Andrew's monotone chain.
Key insight: After sorting by x, the lower hull and upper hull are each built by keeping only clockwise-safe turns: while the last two points plus the new one make a non-clockwise turn, pop. Concatenating both chains (minus endpoints) gives the hull in order.
Complexity: Time O(n log n) for the sort, O(n) for the scan; space O(n).
```java
import java.util.Arrays;
public class L18Q3Hull {
    static long cross(int[] o, int[] a, int[] b) {
        return (long) (a[0] - o[0]) * (b[1] - o[1]) - (long) (a[1] - o[1]) * (b[0] - o[0]);
    }
    public static void main(String[] args) {
        int[][] p = {{0, 0}, {1, 1}, {2, 2}, {0, 2}, {2, 0}, {1, 0}};
        Arrays.sort(p, (x, y) -> x[0] != y[0] ? x[0] - y[0] : x[1] - y[1]);
        int n = p.length, k = 0;
        int[][] h = new int[2 * n][];
        for (int[] q : p) { while (k >= 2 && cross(h[k - 2], h[k - 1], q) <= 0) k--; h[k++] = q; }
        for (int i = n - 2, t = k + 1; i >= 0; i--) {
            while (k >= t && cross(h[k - 2], h[k - 1], p[i]) <= 0) k--;
            h[k++] = p[i];
        }
        String s = "";
        for (int i = 0; i < k - 1; i++) s += "(" + h[i][0] + "," + h[i][1] + ")";
        System.out.println("hull=" + s);
    }
}
```
Observed output: `hull=(0,0)(2,0)(2,2)(0,2)`
Follow-up: Why does popping on <= 0 (rather than < 0) drop collinear edge points, and when would you keep them?

## Checklist
- State the key insight before coding; name the loop invariant.
- Derive time and space bounds from the code structure, not from memory.
