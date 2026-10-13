# Mock Interview: Dancing Links (Algorithm X)

## Q1 — Exact Cover on a Tiny Matrix

**Problem.** Choose rows covering each column exactly once (Sudoku reduces to this).
**Key insight.** Algorithm X: pick a column, try each covering row, cover its columns, recurse; uncover on backtrack. Dancing links makes cover/uncover O(1) pointer surgery.
**Complexity.** Exponential worst case (NP-complete); DLX minimizes the constant.

```java
import java.util.ArrayList;
import java.util.List;
public class DancingQ1 {
    static boolean solve(int[][] m, boolean[] cov, List<Integer> sol) {
        int c = -1;
        for (int j = 0; j < cov.length; j++) if (!cov[j]) { c = j; break; }
        if (c == -1) return true;
        for (int r = 0; r < m.length; r++) {
            if (m[r][c] == 0) continue;
            List<Integer> touched = new ArrayList<>();
            boolean clash = false;
            for (int j = 0; j < cov.length; j++) if (m[r][j] == 1) { if (cov[j]) { clash = true; break; } touched.add(j); }
            if (clash) continue;
            for (int j : touched) cov[j] = true;
            sol.add(r);
            if (solve(m, cov, sol)) return true;
            sol.remove(sol.size() - 1);
            for (int j : touched) cov[j] = false;
        }
        return false;
    }
    public static void main(String[] args) {
        List<Integer> sol = new ArrayList<>();
        solve(new int[][]{{1, 0, 1}, {0, 1, 0}, {1, 1, 0}}, new boolean[3], sol);
        System.out.println(sol);
    }
}
```

Output:

```
[0, 1]
```

## Q2 — Cover/Uncover Symmetry

**Problem.** Why must uncover reverse cover exactly?
**Key insight.** Uncover replays removed links in reverse, restoring the structure bit-for-bit. Asymmetry corrupts iteration deep in search; exact reversal is the correctness argument.
**Complexity.** O(1) per link, both directions.

```java
import java.util.ArrayDeque;
import java.util.Deque;
public class DancingQ2 {
    public static void main(String[] args) {
        Deque<Integer> col = new ArrayDeque<>();
        for (int i = 1; i <= 4; i++) col.addLast(i);
        Deque<Integer> removed = new ArrayDeque<>();
        removed.push(col.removeFirst()); removed.push(col.removeFirst());
        while (!removed.isEmpty()) col.addFirst(removed.pop());
        System.out.println(col);
    }
}
```

Output:

```
[1, 2, 3, 4]
```

## Q3 — Minimum-Remaining-Values Column Choice

**Problem.** Which column should Algorithm X branch on?
**Key insight.** Fewest covering rows first: fewest branches, earliest failure. This one heuristic drives most of DLX's Sudoku/tiling speed.
**Complexity.** Still exponential worst case; far smaller in practice.

```java
public class DancingQ3 {
    public static void main(String[] args) {
        int[][] m = {{1, 0, 1}, {0, 1, 0}, {1, 1, 0}, {0, 1, 1}};
        int best = -1, bestN = Integer.MAX_VALUE;
        for (int j = 0; j < 3; j++) { int n = 0; for (int[] row : m) n += row[j]; if (n < bestN) { bestN = n; best = j; } }
        System.out.println("col=" + best + " options=" + bestN);
    }
}
```

Output:

```
col=0 options=2
```
