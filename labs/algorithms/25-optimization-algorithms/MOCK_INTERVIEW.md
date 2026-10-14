# Mock Interview: Optimization Algorithms

## Q1: Minimize a quadratic with gradient descent

Key insight: step against the gradient, x -= step times f'(x); on a smooth convex quadratic a small fixed step converges linearly.
Complexity: O(iterations) time, O(1) space; oversized steps overshoot and diverge, tiny steps crawl.

```java
public class GradientDescentDemo {
    public static void main(String[] a) {
        double x = 0.0, step = 0.4; // minimize f(x) = (x-3)^2, gradient 2(x-3)
        for (int i = 0; i < 20; i++) x = x - step * 2 * (x - 3);
        System.out.println("x=" + x + " f=" + ((x - 3) * (x - 3)));
    }
}
```

Output:

```text
x=2.9999999999999685 f=9.941619558047801E-28
```

## Q2: Minimize a unimodal function with ternary search

Key insight: comparing two interior points discards the third of the bracket beyond the worse one; repeat until tight.
Complexity: O(iterations) time, O(1) space with a 2/3 shrink factor per round; needs unimodality, else it finds a local valley.

```java
public class TernarySearchDemo {
    static double f(double x) { return (x - 2) * (x - 2) + 1; } // unimodal on [0,6]
    public static void main(String[] a) {
        double lo = 0, hi = 6;
        for (int i = 0; i < 60; i++) {
            double m1 = lo + (hi - lo) / 3, m2 = hi - (hi - lo) / 3;
            if (f(m1) > f(m2)) lo = m1; else hi = m2;
        }
        System.out.println("x=" + ((lo + hi) / 2) + " f=" + f((lo + hi) / 2));
    }
}
```

Output:

```text
x=1.9999999895298797 f=1.0
```

## Q3: Solve a 2-variable linear program by vertex enumeration

Key insight: a bounded 2-variable LP attains its optimum at a feasible vertex, so score the constraint intersections directly.
Complexity: O(vertices) time, O(1) space; teaches the geometry, not production-scale solving.

```java
public class SmallLpDemo {
    public static void main(String[] a) {
        // Max 3x+2y s.t. x+y<=4, 2x+y<=6, x,y>=0: optimum at a vertex.
        double[][] pts = {{0, 0}, {0, 4}, {2, 2}, {3, 0}};
        double best = Double.NEGATIVE_INFINITY, bx = 0, by = 0;
        for (double[] p : pts) { double v = 3 * p[0] + 2 * p[1]; if (v > best) { best = v; bx = p[0]; by = p[1]; } }
        System.out.println("x=" + bx + " y=" + by + " value=" + best);
    }
}
```

Output:

```text
x=2.0 y=2.0 value=10.0
```
