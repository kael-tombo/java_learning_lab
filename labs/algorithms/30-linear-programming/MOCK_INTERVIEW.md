# Mock Interview: Linear Programming

## Q1: Solve a 2-variable LP by vertex enumeration

Key insight: a bounded LP attains its optimum at a vertex of the feasible polygon, so score each constraint intersection directly.
Complexity: O(vertices) time, O(1) space; this shows the geometry behind the simplex method, which walks vertices at scale.

```java
public class VertexLpDemo {
    public static void main(String[] a) {
        // Max 2x+3y s.t. x+2y<=8, 3x+y<=9, x,y>=0: optimum at a vertex.
        double[][] pts = {{0, 0}, {0, 4}, {2, 3}, {3, 0}};
        double best = Double.NEGATIVE_INFINITY, bx = 0, by = 0;
        for (double[] p : pts) { double v = 2 * p[0] + 3 * p[1]; if (v > best) { best = v; bx = p[0]; by = p[1]; } }
        System.out.println("x=" + bx + " y=" + by + " value=" + best);
    }
}
```

Output:

```text
x=2.0 y=3.0 value=13.0
```

## Q2: Check weak duality on a primal-dual pair

Key insight: any feasible dual solution bounds the primal optimum (primal value never exceeds dual value); equal values certify both optimal.
Complexity: O(1) arithmetic here; conceptually, duality turns an optimality proof into one feasible point on each side.

```java
public class DualityDemo {
    public static void main(String[] a) {
        // Primal: max 3x+2y s.t. x+y<=4, x,y>=0. Dual: min 4u s.t. u>=3, u>=2, u>=0.
        double px = 4, py = 0; // primal feasible: 4+0<=4
        double u = 3; // dual feasible: 3>=3 and 3>=2
        double primal = 3 * px + 2 * py, dual = 4 * u; // weak duality: primal<=dual
        System.out.println("primal=" + primal + " dual=" + dual + " gap=" + (dual - primal));
    }
}
```

Output:

```text
primal=12.0 dual=12.0 gap=0.0
```

## Q3: Distinguish infeasible, unbounded, and optimal

Key insight: no feasible vertex means infeasible; a feasible ray improving the objective means unbounded; otherwise the best vertex wins.
Complexity: O(c^2) vertex tests for c constraints plus ray checks; simplex reports the same three statuses at scale.

```java
public class LpStatusDemo {
    // Constraints a*x+b*y<=rhs. Status via vertices + recession-direction test.
    static boolean feas(double x, double y, double[][] c) {
        for (double[] r : c) if (r[0] * x + r[1] * y > r[2] + 1e-9) return false;
        return true;
    }
    static String solve(double cx, double cy, double[][] c) {
        double best = Double.NEGATIVE_INFINITY;
        for (int i = 0; i < c.length; i++) for (int j = i + 1; j < c.length; j++) {
            double d = c[i][0] * c[j][1] - c[j][0] * c[i][1];
            if (Math.abs(d) < 1e-12) continue; // parallel boundaries
            double x = (c[i][2] * c[j][1] - c[j][2] * c[i][1]) / d;
            double y = (c[i][0] * c[j][2] - c[j][0] * c[i][2]) / d;
            if (feas(x, y, c)) best = Math.max(best, cx * x + cy * y);
        }
        if (best == Double.NEGATIVE_INFINITY) return "INFEASIBLE";
        double[][] dirs = {{1, 0}, {0, 1}, {1, 1}};
        for (double[] t : dirs) {
            boolean ray = cx * t[0] + cy * t[1] > 0;
            for (double[] r : c) if (r[0] * t[0] + r[1] * t[1] > 1e-9) ray = false;
            if (ray) return "UNBOUNDED";
        }
        return "OPTIMAL value=" + best;
    }
    public static void main(String[] a) {
        System.out.println(solve(1, 1, new double[][]{{1, 0, -1}, {-1, 0, 0}})); // x<=-1, x>=0
        System.out.println(solve(1, 1, new double[][]{{-1, 0, 0}, {0, -1, 0}})); // x,y>=0
        System.out.println(solve(2, 3, new double[][]{{1, 2, 8}, {3, 1, 9}, {-1, 0, 0}, {0, -1, 0}}));
    }
}
```

Output:

```text
INFEASIBLE
UNBOUNDED
OPTIMAL value=13.0
```
