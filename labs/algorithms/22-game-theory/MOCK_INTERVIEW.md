# Mock Interview: Game Theory

## Q1: Compute the minimax value of a game tree

Key insight: max levels take the maximum of their children, min levels the minimum; recursion bottoms out at leaf payoffs.
Complexity: O(b^d) time for branching factor b and depth d, O(d) stack space.

```java
public class MinimaxDemo {
    static int minimax(int[] leaves, int lo, int hi, boolean maxTurn) {
        if (hi - lo == 1) return leaves[lo];
        int mid = (lo + hi) / 2;
        int l = minimax(leaves, lo, mid, !maxTurn), r = minimax(leaves, mid, hi, !maxTurn);
        return maxTurn ? Math.max(l, r) : Math.min(l, r);
    }
    public static void main(String[] a) {
        System.out.println("value=" + minimax(new int[]{9, 8, 7, 6, 1, 2, 3, 4}, 0, 8, true));
    }
}
```

Output:

```text
value=7
```

## Q2: Add alpha-beta pruning and count the saved visits

Key insight: carry the best secured values (alpha for max, beta for min) downward and skip subtrees that cannot change the outcome.
Complexity: O(b^d) worst case, O(b^(d/2)) with good ordering; 12 visits here against 15 nodes for the full tree.

```java
public class AlphaBetaDemo {
    static int visits;
    static int ab(int[] l, int lo, int hi, boolean max, int alpha, int beta) {
        visits++;
        if (hi - lo == 1) return l[lo];
        int mid = (lo + hi) / 2;
        if (max) {
            int v = Math.max(Integer.MIN_VALUE, ab(l, lo, mid, false, alpha, beta));
            if (v >= beta) return v;
            return Math.max(v, ab(l, mid, hi, false, Math.max(alpha, v), beta));
        }
        int v = Math.min(Integer.MAX_VALUE, ab(l, lo, mid, true, alpha, beta));
        if (v <= alpha) return v;
        return Math.min(v, ab(l, mid, hi, true, alpha, Math.min(beta, v)));
    }
    public static void main(String[] a) {
        int[] leaves = {9, 8, 7, 6, 1, 2, 3, 4};
        int v = ab(leaves, 0, 8, true, Integer.MIN_VALUE, Integer.MAX_VALUE);
        System.out.println("value=" + v + " visits=" + visits);
    }
}
```

Output:

```text
value=7 visits=12
```

## Q3: Find pure Nash equilibria of a 2x2 game

Key insight: a cell is an equilibrium when each choice is a best response to the other, so test every cell against unilateral deviations.
Complexity: O(n^2) checks for an n-by-n game; equilibrium payoffs can still trail the joint optimum.

```java
public class NashDemo {
    public static void main(String[] a) {
        int[][] R = {{3, 0}, {5, 1}}, C = {{3, 5}, {0, 1}};
        for (int r = 0; r < 2; r++) for (int c = 0; c < 2; c++) {
            boolean rb = true, cb = true;
            for (int i = 0; i < 2; i++) { if (R[i][c] > R[r][c]) rb = false; if (C[r][i] > C[r][c]) cb = false; }
            if (rb && cb) System.out.println("equilibrium=(" + r + "," + c + ")");
        }
    }
}
```

Output:

```text
equilibrium=(1,1)
```
