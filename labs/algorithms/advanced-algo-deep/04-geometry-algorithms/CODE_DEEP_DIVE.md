# Code Deep Dive — Geometry Algorithms

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
import java.util.*;

public final class Geo {
    record P(long x, long y) {}

    /** Signed double-area of triangle a,b,c; sign = orientation. */
    static long cross(P a, P b, P c) {
        return (b.x() - a.x()) * (c.y() - a.y()) - (b.y() - a.y()) * (c.x() - a.x());
    }

    /** Andrew's monotone chain; returns CCW hull without repeating the first point. */
    public static List<P> hull(List<P> pts) {
        if (pts.size() <= 1) return new ArrayList<>(pts);
        List<P> s = new ArrayList<>(pts);
        s.sort(Comparator.<P>comparingLong(P::x).thenComparingLong(P::y));
        List<P> lower = new ArrayList<>();
        for (P p : s) {
            while (lower.size() >= 2 && cross(lower.get(lower.size()-2), lower.get(lower.size()-1), p) <= 0)
                lower.remove(lower.size()-1);
            lower.add(p);
        }
        List<P> upper = new ArrayList<>();
        for (int i = s.size()-1; i >= 0; i--) {
            P p = s.get(i);
            while (upper.size() >= 2 && cross(upper.get(upper.size()-2), upper.get(upper.size()-1), p) <= 0)
                upper.remove(upper.size()-1);
            upper.add(p);
        }
        lower.remove(lower.size()-1); upper.remove(upper.size()-1);
        List<P> h = new ArrayList<>(lower); h.addAll(upper);
        return h;
    }

    /** Point-in-polygon by ray casting with the half-open y rule. */
    public static boolean inside(List<P> poly, P q) {
        boolean in = false;
        for (int i = 0, j = poly.size()-1; i < poly.size(); j = i++) {
            P a = poly.get(i), b = poly.get(j);
            if ((a.y() > q.y()) != (b.y() > q.y())
                && q.x() < (b.x()-a.x())*(q.y()-a.y())/(b.y()-a.y()) + a.x())
                in = !in;
        }
        return in;
    }
}
```

## Pitfalls

- Using slopes divides by zero on vertical segments and loses exactness — use the cross product.
- 32-bit overflow in (B.x-A.x)*(C.y-A.y) — promote to long first.
- The collinearity policy (< 0 vs <= 0) changes which boundary points survive; document it.
- A ray through a vertex needs the half-open y-interval rule or it double-counts.
- Forgetting to dedup points before Andrew's scan creates zero-length edges.
- Assuming the hull of collinear points is a polygon — it is a segment; handle it as a special case.

## Why the bounds hold

- **Orientation predicate**: Θ(1) time, Θ(1) — exact with long arithmetic.
- **Monotone-chain hull**: Θ(n log n) time, Θ(n) — sort + linear scan.
- **Segment intersection test**: Θ(1) time, Θ(1) — four orientation signs.
- **Point-in-polygon**: Θ(n) time, Θ(1) — one pass over edges.
- **Closest pair**: Θ(n log n) time, Θ(n) — divide and conquer.
- **All-pairs hull**: Θ(n²) time, Θ(n) — gift wrapping baseline.

## Takeaway

# Theory — Computational Geometry
